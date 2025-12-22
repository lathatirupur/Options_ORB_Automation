# Options_ORB_Automation
Options Opening Range Breakout 15 mins strategy automation

FULLY AUTOMATED ORB PAPER TRADING with Kite API, including:

✔ Tick-by-tick WebSocket
✔ 15-min ORB (5-min candles)
✔ 45-sec hold
✔ Volume filter
✔ Auto ATM strike selection (CE & PE)
✔ Re-entry logic
✔ Kill switch + daily max loss
✔ Automatic Excel (CSV) logging

Project Structure
orb_paper_trading/
│
├── config.py
├── kite_connection.py
├── instruments.py
├── orb_logic.py
├── paper_engine.py
├── logger.py
├── main.py
│
├── paper_trades.csv        ← auto-created
├── daily_summary.csv       ← auto-created
