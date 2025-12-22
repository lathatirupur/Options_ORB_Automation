from kite_connection import kite, kws
from instruments import load_nifty_options, get_atm_option
from orb_logic import compute_orb, check_hold, update_volume, volume_ok
from paper_engine import (
    paper_entry,
    paper_exit,
    in_trade,
    kill_switch,
    can_reenter,
    check_exit,
    symbol
)
from config import (
    NIFTY_TOKEN,
    HOLD_SECONDS,
    VOLUME_MULTIPLIER
)
from logger import init_logs

# ---------------- INIT ---------------- #

init_logs()
OPTIONS = load_nifty_options(kite)

# Compute ORB automatically (9:15–9:30)
orb_high, orb_low = compute_orb(kite, NIFTY_TOKEN)
print(f"ORB READY | HIGH={orb_high} LOW={orb_low}")

# ---------------- SAFE LTP ---------------- #

def safe_ltp(symbol):
    try:
        return kite.ltp(symbol)[symbol]["last_price"]
    except Exception as e:
        print("LTP error:", e)
        return None

# ---------------- TICK HANDLER ---------------- #

def on_ticks(ws, ticks):
    try:
        if kill_switch:
            return

        tick = ticks[0]
        spot_price = tick["last_price"]

        # Update rolling volume buckets
        update_volume(tick)

        # ---------------- ENTRY ---------------- #
        if not in_trade and can_reenter():

            # BULLISH ORB
            if (
                spot_price > orb_high and
                check_hold(spot_price, orb_high, HOLD_SECONDS, "CE") and
                volume_ok(VOLUME_MULTIPLIER)
            ):
                sym = get_atm_option(OPTIONS, spot_price, "CE")
                opt_price = safe_ltp(f"NFO:{sym}")
                if opt_price:
                    paper_entry(opt_price, sym)

            # BEARISH ORB
            elif (
                spot_price < orb_low and
                check_hold(spot_price, orb_low, HOLD_SECONDS, "PE") and
                volume_ok(VOLUME_MULTIPLIER)
            ):
                sym = get_atm_option(OPTIONS, spot_price, "PE")
                opt_price = safe_ltp(f"NFO:{sym}")
                if opt_price:
                    paper_entry(opt_price, sym)

        # ---------------- EXIT ---------------- #
        elif in_trade:
            opt_price = safe_ltp(f"NFO:{symbol}")
            if opt_price:
                reason = check_exit(opt_price)
                if reason:
                    paper_exit(opt_price, reason)

    except Exception as e:
        print("Tick processing error:", e)

# ---------------- WEBSOCKET ---------------- #

def on_connect(ws, response):
    ws.subscribe([NIFTY_TOKEN])
    ws.set_mode(ws.MODE_LTP, [NIFTY_TOKEN])

kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect()
