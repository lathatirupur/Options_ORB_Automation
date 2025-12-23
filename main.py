from datetime import datetime, time
import atexit

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
from config import (
    NIFTY_TOKEN,
    MIN_BREAKOUT_POINTS,
    HOLD_SECONDS_FIRST,
    HOLD_SECONDS_REENTRY,
    VOLUME_MULTIPLIER
)
from logger import init_logs, generate_daily_summary

# =====================
# AUTO DAILY SUMMARY
# =====================
atexit.register(generate_daily_summary)

# =====================
# TIME WINDOWS
# =====================
ENTRY_START_TIME = time(9, 30)
ENTRY_END_TIME   = time(11, 0)
REENTRY_CUTOFF_TIME = time(10, 45)

def within_entry_window():
    now = datetime.now().time()
    return ENTRY_START_TIME <= now <= ENTRY_END_TIME

def within_reentry_window():
    now = datetime.now().time()
    return now <= REENTRY_CUTOFF_TIME

# =====================
# DEBUG LOGGER
# =====================
def debug_skip(reason):
    print(f"[SKIP {datetime.now().time()}] {reason}")

# =====================
# INIT
# =====================
init_logs()
OPTIONS = load_nifty_options(kite)

orb_high, orb_low = compute_orb(kite, NIFTY_TOKEN)
print(f"ORB READY | High={orb_high} Low={orb_low}")

# =====================
# SAFE LTP
# =====================
def safe_ltp(trading_symbol):
    try:
        return kite.ltp(trading_symbol)[trading_symbol]["last_price"]
    except:
        return None

# =====================
# TICK HANDLER
# =====================
def on_ticks(ws, ticks):
    if kill_switch:
        debug_skip("Kill switch active")
        return

    tick = ticks[0]
    spot_price = tick["last_price"]

    update_volume(tick)
    session_volume = current_session_volume()

    # ================= ENTRY =================
    if not in_trade:

        if not within_entry_window():
            debug_skip("Outside entry time window")
            return

        if not can_reenter():
            debug_skip("Re-entry cooldown active")
            return

        if first_breakout_volume and not within_reentry_window():
            debug_skip("Re-entry cutoff time passed (10:45)")
            return

        hold_time = HOLD_SECONDS_REENTRY if first_breakout_volume else HOLD_SECONDS_FIRST

        # -------- CE --------
        if spot_price > orb_high + MIN_BREAKOUT_POINTS:

            if not check_hold(spot_price, orb_high, hold_time, "CE"):
                debug_skip("CE hold condition not met")
                return

            if not volume_ok(VOLUME_MULTIPLIER):
                debug_skip("CE volume condition failed")
                return

            if first_breakout_volume and session_volume <= first_breakout_volume:
                debug_skip("CE re-entry volume not higher than first breakout")
                return

            sym = get_atm_option(OPTIONS, spot_price, "CE")
            opt_price = safe_ltp(f"NFO:{sym}")
            if opt_price:
                paper_entry(opt_price, sym, "CE", session_volume)
                return

        # -------- PE --------
        elif spot_price < orb_low - MIN_BREAKOUT_POINTS:

            if not check_hold(spot_price, orb_low, hold_time, "PE"):
                debug_skip("PE hold condition not met")
                return

            if not volume_ok(VOLUME_MULTIPLIER):
                debug_skip("PE volume condition failed")
                return

            if first_breakout_volume and session_volume <= first_breakout_volume:
                debug_skip("PE re-entry volume not higher than first breakout")
                return

            sym = get_atm_option(OPTIONS, spot_price, "PE")
            opt_price = safe_ltp(f"NFO:{sym}")
            if opt_price:
                paper_entry(opt_price, sym, "PE", session_volume)
                return

    # ================= EXIT =================
    else:

        if direction == "CE" and spot_price <= orb_high:
            paper_exit(safe_ltp(f"NFO:{symbol}"), "Spot Re-entry SL")
            return

        if direction == "PE" and spot_price >= orb_low:
            paper_exit(safe_ltp(f"NFO:{symbol}"), "Spot Re-entry SL")
            return

        opt_price = safe_ltp(f"NFO:{symbol}")
        if opt_price:
            reason = check_exit(opt_price)
            if reason:
                paper_exit(opt_price, reason)

# =====================
# WS CONNECT
# =====================
def on_connect(ws, response):
    ws.subscribe([NIFTY_TOKEN])
    ws.set_mode(ws.MODE_LTP, [NIFTY_TOKEN])

kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect()
