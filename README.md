# Options_ORB_Automation

Fully automated Opening Range Breakout (ORB) strategy for NIFTY options  
with *tick-by-tick data*, automatic ATM strike selection, re-entry logic, kill-switch  
and automatic Excel (CSV) logging — currently in **paper-trading mode**.

---

## 🧠 WHAT THIS PROJECT DOES

This project automates the **15-minute Opening Range Breakout (ORB)** strategy for NIFTY options using tick data from the Kite API.  
It includes:

✔ Tick-by-tick WebSocket data  
✔ 15-min ORB range (built from 5-min candles)  
✔ 45-second breakout hold logic  
✔ Session-only volume filter  
✔ Automatic ATM strike selection (CE & PE)  
✔ Re-entry logic (1 repeat trade allowed)  
✔ Kill-switch with **daily max loss**  
✔ Auto Excel/CSV logging (trade log + daily summary)

This is a **paper-trading engine** designed for validation before going live.

---

## 📁 PROJECT STRUCTURE

orb_paper_trading/
├── config.py # All strategy + API config
├── kite_connection.py # Kite Connect + WebSocket setup
├── instruments.py # NIFTY option strike selector
├── orb_logic.py # ORB & hold logic
├── paper_engine.py # Entry/exit + kill switch
├── logger.py # CSV logging + summary
├── main.py # Tick handler + strategy engine
├── paper_trades.csv # Auto-generated trade log
└── daily_summary.csv # Auto-generated daily P&L


---

## 🚀 HOW TO RUN (PAPER MODE)

1. Install dependencies:

   ```bash
   pip install kiteconnect pandas


Fill in config.py with your Kite API key & token.

Run the bot:

python main.py


After the session, open:

paper_trades.csv → Detailed trade log

daily_summary.csv → Daily performance summary

🧠 STRATEGY RULES

Entry conditions

Spot breaks above ORB high (for CE) or below ORB low (for PE)

Price stays on that side for 45 seconds

Heavy enough volume compared with session data

Exit conditions

Spot re-enters ORB range → Exit (SL)

Target (fixed or trailing) hit → Exit

Kill-switch triggers → Stop trading

📌 NOTES

This repo is paper-trading only. ✔

Real (broker) order placement is not implemented yet.

Logging is automatic; no manual logging needed.

📈 NEXT STEPS

Once validated, you can:
✔ Add real orders
✔ Add PUT & CALL simultaneous handling
✔ Enhance analytics dashboards
✔ Deploy on VPS for live monitoring

❗ DISCLAIMER

Trading financial markets involves risk. This bot is for educational and testing purposes.
Do NOT deploy without proper understanding and validation.


---

## 🛠️ SUGGESTED TWEAKS FOR YOUR PROJECT

Here are a few *improvements you might want to add* to make the code more robust:

### 1️⃣ **Automatically compute ORB range**
Right now `orb_high` and `orb_low` might be manually set — automate them from 5-min candles using Kite historical API.

> Build 5-min ORB from 9:15–9:30 each day programmatically.

---

### 2️⃣ **Add PUT side handling**
Your current `main.py` only checks bullish direction.  
Add bearish entry for PE as we discussed earlier.

---

### 3️⃣ **Volume filter integration**
Ensure `volume_ok()` logic uses session volumes — right now there’s no such function in main.py.

> Add a rolling volume buffer via ticks & 5-min buckets.

---

### 4️⃣ **Trailing SL / Target logic**
Right now paper exit is only spot re-entry SL.  
Add dynamic target + trailing SL for more realistic backtests.

---

### 5️⃣ **Re-entry cooldown**
You should enforce a short cooldown + global re-entry count — safe guard against rapid second entries.

---

### 6️⃣ **Error handling**
Wrap API calls (`kite.ltp`, websocket) with try/except to handle disconnects.

---
