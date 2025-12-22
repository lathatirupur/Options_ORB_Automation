from kite_connection import kite, kws
from instruments import load_nifty_options, get_atm_option
from orb_logic import check_hold
from paper_engine import paper_entry, paper_exit, in_trade, kill_switch
from config import NIFTY_TOKEN, HOLD_SECONDS
from logger import init_logs

init_logs()
OPTIONS = load_nifty_options(kite)

orb_high = None
orb_low = None

def on_ticks(ws, ticks):
    global orb_high, orb_low

    price = ticks[0]["last_price"]

    # ORB already calculated manually at 9:30
    if kill_switch:
        return

    if not in_trade:
        if check_hold(price, orb_high, HOLD_SECONDS):
            sym = get_atm_option(OPTIONS, price, "CE")
            opt_price = kite.ltp(f"NFO:{sym}")[f"NFO:{sym}"]["last_price"]
            paper_entry(opt_price, sym)

    else:
        if price < orb_high:
            opt_price = kite.ltp(f"NFO:{symbol}")[f"NFO:{symbol}"]["last_price"]
            paper_exit(opt_price, "Spot SL")

def on_connect(ws, response):
    ws.subscribe([NIFTY_TOKEN])
    ws.set_mode(ws.MODE_LTP, [NIFTY_TOKEN])

kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect()
