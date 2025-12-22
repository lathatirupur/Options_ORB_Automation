from kite_connection import kite, kws
from instruments import load_nifty_options, get_atm_option
from orb_logic import (
    compute_orb,
    check_hold,
    update_volume,
    volume_ok,
    current_session_volume
)
from paper_engine import (
    paper_entry,
    paper_exit,
    check_exit,
    can_reenter,
    in_trade,
    kill_switch,
    symbol,
    direction,
    first_breakout_volume
)
from config import *
from logger import init_logs

# ---- INIT ----
init_logs()
OPTIONS = load_nifty_options(kite)

orb_high, orb_low = compute_orb(kite, NIFTY_TOKEN)
print(f"ORB READY | High={orb_high} Low={orb_low}")


def safe_ltp(trading_symbol):
    try:
        return kite.ltp(trading_symbol)[trading_symbol]["last_price"]
    except:
        return None


def on_ticks(ws, ticks):
    if kill_switch:
        return

    tick = ticks[0]
    spot_price = tick["last_price"]

    update_volume(tick)
    session_volume = current_session_volume()

    # ================= ENTRY =================
    if not in_trade and can_reenter():

        hold_time = HOLD_SECONDS_REENTRY if first_breakout_volume else HOLD_SECONDS_FIRST

        # ---- CE ----
        if (
            spot_price > orb_high + MIN_BREAKOUT_POINTS and
            check_hold(spot_price, orb_high, hold_time, "CE") and
            volume_ok(VOLUME_MULTIPLIER)
        ):
            if first_breakout_volume and session_volume <= first_breakout_volume:
                return

            sym = get_atm_option(OPTIONS, spot_price, "CE")
            opt_price = safe_ltp(f"NFO:{sym}")
            if opt_price:
                paper_entry(opt_price, sym, "CE", session_volume)

        # ---- PE ----
        elif (
            spot_price < orb_low - MIN_BREAKOUT_POINTS and
            check_hold(spot_price, orb_low, hold_time, "PE") and
            volume_ok(VOLUME_MULTIPLIER)
        ):
            if first_breakout_volume and session_volume <= first_breakout_volume:
                return

            sym = get_atm_option(OPTIONS, spot_price, "PE")
            opt_price = safe_ltp(f"NFO:{sym}")
            if opt_price:
                paper_entry(opt_price, sym, "PE", session_volume)

    # ================= EXIT =================
    elif in_trade:

        # PRIORITY-1: Spot re-entry
        if direction == "CE" and spot_price <= orb_high:
            paper_exit(safe_ltp(f"NFO:{symbol}"), "Spot Re-entry SL")
            return

        if direction == "PE" and spot_price >= orb_low:
            paper_exit(safe_ltp(f"NFO:{symbol}"), "Spot Re-entry SL")
            return

        # PRIORITY-2: R-based trailing
        opt_price = safe_ltp(f"NFO:{symbol}")
        if opt_price:
            reason = check_exit(opt_price)
            if reason:
                paper_exit(opt_price, reason)


def on_connect(ws, response):
    ws.subscribe([NIFTY_TOKEN])
    ws.set_mode(ws.MODE_LTP, [NIFTY_TOKEN])


kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect()
