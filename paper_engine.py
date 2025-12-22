from datetime import datetime
from config import LOT_SIZE, DAILY_MAX_LOSS
from logger import log_trade, update_summary

in_trade = False
entry_price = None
entry_time = None
symbol = None
daily_pnl = 0
kill_switch = False

def paper_entry(price, sym):
    global in_trade, entry_price, entry_time, symbol
    in_trade = True
    entry_price = price
    entry_time = datetime.now()
    symbol = sym

def paper_exit(price, reason):
    global in_trade, daily_pnl, kill_switch
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

    if daily_pnl <= -DAILY_MAX_LOSS:
        kill_switch = True
