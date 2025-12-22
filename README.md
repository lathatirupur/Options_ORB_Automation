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
├── config.py (ALL SETTINGS HERE)
├── kite_connection.py (Kite Setup)
├── instruments.py (AUTO STRIKE SELECTION)
├── orb_logic.py (ORB + HOLD + VOLUME)
├── paper_engine.py (ENTRY / EXIT / RISK)
├── logger.py (EXCEL AUTO LOG)
├── main.py (FULL AUTO ENGINE)
│
├── paper_trades.csv        ← auto-created
├── daily_summary.csv       ← auto-created

HOW TO RUN (STEP-BY-STEP)
pip install kiteconnect pandas
python main.py

📂 Open:
paper_trades.csv → Trade-by-trade journal
daily_summary.csv → Daily P&L
