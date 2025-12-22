from datetime import datetime
from config import LOT_SIZE, DAILY_MAX_LOSS, RISK_POINTS, TARGET_MULTIPLIER, REENTRY_COOLDOWN
from logger import log_trade, update_summary

in_trade = False
entry_price = None
entry_time = None
symbol = None
trail_sl = None
daily_pnl = 0
kill_switch = False
reentry_used = False
last_exit_time = None

def can_reenter():
    if not last_exit_time:
        return True
    return (datetime.now() - last_exit_time).seconds > REENTRY_COOLDOWN

def paper_entry(price, sym):
    global in_trade, entry_price, entry_time, symbol, trail_sl
    in_trade = True
    entry_price = price
    entry_time = datetime.now()
    symbol = sym
    trail_sl = price - RISK_POINTS

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
    last_exit_time = datetime.now()
    reentry_used = True

    if daily_pnl <= -DAILY_MAX_LOSS:
        kill_switch = True

def check_exit(current_price):
    global trail_sl

    if current_price <= trail_sl:
        return "Trailing SL"

    if current_price >= entry_price + (RISK_POINTS * TARGET_MULTIPLIER):
        return "Target Hit"

    if current_price >= entry_price + RISK_POINTS:
        trail_sl = entry_price

    return None
