from datetime import datetime
from config import (
    LOT_SIZE,
    DAILY_MAX_LOSS,
    RISK_POINTS,
    REENTRY_COOLDOWN
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


# ---- Entry ----
def paper_entry(price, sym, trade_direction):
    global in_trade, entry_price, entry_time, symbol, direction, trail_sl

    in_trade = True
    entry_price = price
    entry_time = datetime.now()
    symbol = sym
    direction = trade_direction

    # Initial hard SL = 1R
    trail_sl = entry_price - RISK_POINTS


# ---- Exit ----
def paper_exit(price, reason):
    global in_trade, daily_pnl, kill_switch, reentry_used, last_exit_time

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

    if daily_pnl <= -DAILY_MAX_LOSS:
        kill_switch = True


# ---- Re-entry guard ----
def can_reenter():
    if reentry_used is False:
        return True
    if not last_exit_time:
        return False
    return (datetime.now() - last_exit_time).seconds >= REENTRY_COOLDOWN


# ---- Progressive R-based trailing SL ----
def check_exit(current_price):
    """
    Priority-2 exit:
    Progressive + dynamic R-based trailing SL.
    Exit ONLY on trailing SL hit.
    """

    global trail_sl, entry_price

    R = RISK_POINTS
    move_from_entry = current_price - entry_price

    # ---- Initial R locking ----
    if move_from_entry >= 4 * R:
        completed_r_multiples = int(move_from_entry / R)
        locked_profit_r = completed_r_multiples - 1
        trail_sl = entry_price + (locked_profit_r * R)

    elif move_from_entry >= 3 * R:
        trail_sl = entry_price + (2 * R)

    elif move_from_entry >= 2 * R:
        trail_sl = entry_price + (1 * R)

    elif move_from_entry >= 1.5 * R:
        trail_sl = entry_price + (0.5 * R)

    elif move_from_entry >= 1 * R:
        trail_sl = entry_price  # cost-to-cost

    # ---- Exit check ----
    if current_price <= trail_sl:
        return "Trailing SL Hit"

    return None
