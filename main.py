from kite_connection import kite, kws
from instruments import load_nifty_options, get_atm_option
from orb_logic import (
    compute_orb,
    check_hold,
    update_volume,
    volume_ok
)
from paper_engine import (
    paper_entry,
    paper_exit,
    check_exit,
    can_reenter,
    in_trade,
    kill_switch,
    symbol,
    direction
)
from config import (
    NIFTY_TOKEN,
    HOLD_SECONDS,
    VOLUME_MULTIPLIER
)
from logger import init_logs

# ---- INIT ----
init_logs()
OPTIONS = load_nifty_options(kite)

orb_high, orb_low = compute_orb(kite, NIFTY_TOKEN)
print(f"ORB READY | High={orb_high} Low={orb_low}")


def safe_ltp(trading_symbol):
    try:
        return kite.ltp(trading_symbol)[trading_symbol]["last_price"]
    except Exception as e:
        print("LTP error:", e)
        return None


# ---- Tick Handler ----
def on_ticks(ws, ticks):
    global in_trade

    try:
        if kill_switch:
            return

        tick = ticks[0]
        spot_price = tick["last_price"]

        update_volume(tick)

        # ==========================
        # ENTRY LOGIC
        # ==========================
        if not in_trade and can_reenter():

            # ---- CE breakout ----
            if (
                spot_price > orb_high and
                check_hold(spot_price, orb_high, HOLD_SECONDS, "CE") and
                volume_ok(VOLUME_MULTIPLIER)
            ):
                sym = get_atm_option(OPTIONS, spot_price, "CE")
                opt_price = safe_ltp(f"NFO:{sym}")
                if opt_price:
                    paper_entry(opt_price, sym, "CE")

            # ---- PE breakout ----
            elif (
                spot_price < orb_low and
                check_hold(spot_price, orb_low, HOLD_SECONDS, "PE") and
                volume_ok(VOLUME_MULTIPLIER)
            ):
                sym = get_atm_option(OPTIONS, spot_price, "PE")
                opt_price = safe_ltp(f"NFO:{sym}")
                if opt_price:
                    paper_entry(opt_price, sym, "PE")

        # ==========================
        # EXIT LOGIC
        # ==========================
        elif in_trade:

            # PRIORITY 1: Spot re-entry (IMMEDIATE EXIT)
            if direction == "CE" and spot_price <= orb_high:
                opt_price = safe_ltp(f"NFO:{symbol}")
                if opt_price:
                    paper_exit(opt_price, "Spot Re-entry SL")
                return

            if direction == "PE" and spot_price >= orb_low:
                opt_price = safe_ltp(f"NFO:{symbol}")
                if opt_price:
                    paper_exit(opt_price, "Spot Re-entry SL")
                return

            # PRIORITY 2: R-based trailing SL
            opt_price = safe_ltp(f"NFO:{symbol}")
            if opt_price:
                exit_reason = check_exit(opt_price)
                if exit_reason:
                    paper_exit(opt_price, exit_reason)

    except Exception as e:
        print("Tick processing error:", e)


# ---- WebSocket ----
def on_connect(ws, response):
    ws.subscribe([NIFTY_TOKEN])
    ws.set_mode(ws.MODE_LTP, [NIFTY_TOKEN])


kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect()
