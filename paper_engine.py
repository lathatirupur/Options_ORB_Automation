from datetime import datetime
from config import (
    LOT_SIZE,
    DAILY_MAX_LOSS,
    RISK_POINTS,
    REENTRY_COOLDOWN,
    MAX_SL_PER_DAY
)
from logger import log_trade, update_summary

# ---- Trade State ----
in_trade = False
entry_price = None
entry_time = None
symbol = None
direction = None

trail_sl = None
daily_pnl = 0
kill_switch = False

reentry_used = False
last_exit_time = None
first_breakout_volume = None
sl_count = 0


def reset_daily_state():
    global reentry_used, first_breakout_volume, sl_count
    reentry_used = False
    first_breakout_volume = None
    sl_count = 0


def can_reenter():
    if not reentry_used:
        return True
    if not last_exit_time:
        return False
    return (datetime.now() - last_exit_time).seconds >= REENTRY_COOLDOWN


def paper_entry(price, sym, trade_direction, breakout_volume):
    global in_trade, entry_price, entry_time, symbol, direction, trail_sl, first_breakout_volume

    in_trade = True
    entry_price = price
    entry_time = datetime.now()
    symbol = sym
    direction = trade_direction

    trail_sl = entry_price - RISK_POINTS

    if first_breakout_volume is None:
        first_breakout_volume = breakout_volume


def paper_exit(price, reason):
    global in_trade, daily_pnl, kill_switch, reentry_used, last_exit_time, sl_count

    pnl = (price - entry_price) * LOT_SIZE
    daily_pnl += pnl

    log_trade([
        entry_time.date(),
        entry_time.time(),
        datetime.now().time(),
        symbol,
        entry_price,
        price,
        pnl,
        reason
    ])

    update_summary()

    in_trade = False
    reentry_used = True
    last_exit_time = datetime.now()

    if "SL" in reason:
        sl_count += 1

    if sl_count >= MAX_SL_PER_DAY or daily_pnl <= -DAILY_MAX_LOSS:
        kill_switch = True


def check_exit(current_price):
    """
    Priority-2 exit: Progressive + dynamic R-based trailing
    """
    global trail_sl

    R = RISK_POINTS
    move = current_price - entry_price

    if move >= 4 * R:
        completed_r = int(move / R)
        locked_r = completed_r - 1
        trail_sl = entry_price + (locked_r * R)

    elif move >= 3 * R:
        trail_sl = entry_price + (2 * R)

    elif move >= 2 * R:
        trail_sl = entry_price + (1 * R)

    elif move >= 1.5 * R:
        trail_sl = entry_price + (0.5 * R)

    elif move >= 1 * R:
        trail_sl = entry_price

    if current_price <= trail_sl:
        return "Trailing SL Hit"

    return None
