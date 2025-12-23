# Options_ORB_Automation

A **fully automated Opening Range Breakout (ORB)** system for **NIFTY option buying**,  
built using **tick-by-tick Kite WebSocket data**, with **strict rule enforcement**,  
**paper trading**, and **automated performance analytics**.

This project is designed to **validate ORB behaviour objectively**  
before any real-money deployment.

---

## 🧠 WHAT THIS PROJECT DOES

- Trades **NIFTY ATM options** using a **15-minute ORB** (9:15–9:30)
- Uses **spot price** for structure and stop-loss decisions
- Executes **tick-by-tick** (no candle-close dependency)
- Removes emotional execution via automation
- Logs every trade and generates **intraday & end-of-day summaries**
- Provides a foundation to evaluate **strategy health**, not just P&L

> ⚠️ Current mode: **Paper trading only** (no real orders placed)

---

## ✅ KEY FEATURES

✔ Tick-by-tick WebSocket data  
✔ Automatic ORB calculation (9:15–9:30)  
✔ Decisive breakout + hold validation  
✔ CE & PE handling  
✔ Session-only volume filter  
✔ Automatic ATM strike selection  
✔ **Spot re-entry as priority-1 SL**  
✔ **Progressive + dynamic R-based trailing SL**  
✔ One re-entry per direction (anti-chop)  
✔ Higher volume required on re-entry  
✔ Time-based entry filters  
✔ Daily SL-based kill switch  
✔ CSV-based paper trading (Excel friendly)  
✔ Auto-generated intraday & daily summaries  

---

## ⏱️ TRADING TIME RULES

**New Entries**
- Allowed only between **9:30 – 11:00 AM**

**Re-Entries**
- Allowed only until **10:45 AM**
- Only **one re-entry per direction**
- Re-entry must show **higher volume** than the first breakout

**Open Trades**
- No forced exit based on time  
- Trades are managed until SL or trailing exit

---

## 📈 STRATEGY LOGIC

### ORB DEFINITION
- Opening Range = **first 3 × 5-minute candles** (9:15–9:30)
- ORB High & Low computed automatically from historical data

---

### ENTRY CONDITIONS (ALL MUST BE TRUE)

**For CE**
- Spot breaks **above ORB High + buffer**
- Price **holds above ORB** for:
  - 45 seconds (first entry)
  - 60 seconds (re-entry)
- Price does **not snap back** into ORB during hold
- Volume expands vs session average
- Entry time within allowed window

**For PE**
- Mirror logic below ORB Low

---

### EXIT CONDITIONS (STRICT PRIORITY)

**Priority-1: Structural SL**
- Spot **re-enters ORB range**
- Immediate exit (no candle wait)

**Priority-2: Profit Protection**
- Progressive R-based trailing SL
- Dynamic ratcheting beyond +4R
- No fixed profit cap

**Risk Controls**
- Stop trading after **2 SLs per day**
- Daily P&L kill switch as backup

---

## 🔁 RE-ENTRY RULES (ANTI-CHOP)

- Only **ONE re-entry per direction**
- Re-entry must:
  - Hold longer (60s)
  - Show **higher volume than first breakout**
  - Occur before **10:45 AM**
- Cooldown enforced between attempts

---

## 📊 LOGGING & ANALYTICS

All trading is **paper-based** and logged automatically.

### Files Generated

| File | Purpose |
|----|-------|
| `paper_trades.csv` | Raw trade-by-trade log |
| `intraday_summary.csv` | Rolling intraday P&L + trade count |
| `daily_summary.csv` | End-of-day performance snapshot |

### Daily Summary Includes
- Trades taken
- Wins / losses / breakeven
- Net P&L
- Max win / max loss
- SL count

All files are **Excel friendly**.

---

## 📁 PROJECT STRUCTURE
```
Options_ORB_Automation/
├── config.py              # Strategy parameters & API config
├── kite_connection.py     # Kite Connect + WebSocket setup
├── instruments.py         # ATM option strike selection
├── orb_logic.py           # ORB, hold, and volume logic
├── paper_engine.py        # Entry/exit, trailing SL, kill switch
├── logger.py              # Trade logging + summaries
├── main.py                # Tick handler + strategy engine
├── paper_trades.csv       # Auto-generated trade log
├── intraday_summary.csv   # Auto-generated intraday stats
└── daily_summary.csv      # Auto-generated daily summary
```

---

## 🚀 HOW TO RUN (PAPER MODE)

1️⃣ Install Dependencies
```
pip install kiteconnect pandas
```
2️⃣ Configure API  

Fill in your Kite credentials in config.py:

API_KEY = "your_key"  
ACCESS_TOKEN = "your_token"

3️⃣ Run the Bot  
```
python main.py
```
4️⃣ Review Results  

paper_trades.csv → Detailed trade-by-trade history  
daily_summary.csv → Day-wise performance summary  

All files are auto-generated and Excel-friendly.

---

## 🧠 STRATEGY PHILOSOPHY

- Low win-rate, high R-multiple system  
- Edge comes from trend days, not frequency  
- Focus is on behavioural validation, not curve fitting  
- Designed to survive choppy market regimes via strict filters  

This system prioritizes process quality and rule adherence over short-term profits.

---

## ⚠️ IMPORTANT NOTES

- This repository is paper trading only  
- No live orders are placed  
- Do NOT deploy live without:
  - Multi-week paper validation  
  - Drawdown analysis  
  - Strategy health review  

---

## 📈 NEXT STEPS (OPTIONAL)

Once validated, you can extend this system to:

- Live order placement
  
---

## ❗ DISCLAIMER

Trading financial markets involves substantial risk.  
This project is for educational and testing purposes only.  

The author is not responsible for any financial losses incurred by using this code.
