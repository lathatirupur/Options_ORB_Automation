import pandas as pd
from pathlib import Path
from datetime import datetime

# =====================
# FILES
# =====================
TRADE_FILE = "paper_trades.csv"
INTRADAY_SUMMARY_FILE = "intraday_summary.csv"
DAILY_SUMMARY_FILE = "daily_summary.csv"

# =====================
# INIT
# =====================
def init_logs():
    # Trade log
    if not Path(TRADE_FILE).exists():
        pd.DataFrame(columns=[
            "Date",
            "EntryTime",
            "ExitTime",
            "Symbol",
            "Entry",
            "Exit",
            "PnL",
            "Reason"
        ]).to_csv(TRADE_FILE, index=False)

    # Intraday rolling summary
    if not Path(INTRADAY_SUMMARY_FILE).exists():
        pd.DataFrame(columns=[
            "Date",
            "Trades",
            "NetPnL"
        ]).to_csv(INTRADAY_SUMMARY_FILE, index=False)

    # End-of-day summary
    if not Path(DAILY_SUMMARY_FILE).exists():
        pd.DataFrame(columns=[
            "Date",
            "Trades",
            "Wins",
            "Losses",
            "Breakeven",
            "NetPnL",
            "MaxProfit",
            "MaxLoss",
            "SL_Count"
        ]).to_csv(DAILY_SUMMARY_FILE, index=False)

# =====================
# TRADE LOGGER
# =====================
def log_trade(row):
    df = pd.read_csv(TRADE_FILE)
    df.loc[len(df)] = row
    df.to_csv(TRADE_FILE, index=False)

    # Update lightweight intraday stats after each trade
    update_summary()

# =====================
# INTRADAY ROLLING SUMMARY
# =====================
def update_summary():
    """
    Lightweight summary updated AFTER EACH TRADE.
    Purpose: quick intraday visibility (PnL + trade count only).
    """
    df = pd.read_csv(TRADE_FILE)
    if df.empty:
        return

    today = datetime.now().date()
    day_df = df[df["Date"] == today]

    if day_df.empty:
        return

    summary = {
        "Date": today,
        "Trades": len(day_df),
        "NetPnL": day_df["PnL"].sum()
    }

    summary_df = pd.read_csv(INTRADAY_SUMMARY_FILE)
    summary_df = summary_df[summary_df["Date"] != today]
    summary_df.loc[len(summary_df)] = summary
    summary_df.to_csv(INTRADAY_SUMMARY_FILE, index=False)

# =====================
# END-OF-DAY SUMMARY
# =====================
def generate_daily_summary():
    """
    Final end-of-day performance summary.
    Should be called ONCE after market close or program exit.
    """
    df = pd.read_csv(TRADE_FILE)
    if df.empty:
        return

    today = df.iloc[-1]["Date"]
    day_df = df[df["Date"] == today]

    if day_df.empty:
        return

    trades = len(day_df)
    wins = (day_df["PnL"] > 0).sum()
    losses = (day_df["PnL"] < 0).sum()
    breakeven = trades - wins - losses

    net_pnl = day_df["PnL"].sum()
    max_profit = day_df["PnL"].max()
    max_loss = day_df["PnL"].min()
    sl_count = day_df["Reason"].str.contains("SL", na=False).sum()

    summary = {
        "Date": today,
        "Trades": trades,
        "Wins": wins,
        "Losses": losses,
        "Breakeven": breakeven,
        "NetPnL": net_pnl,
        "MaxProfit": max_profit,
        "MaxLoss": max_loss,
        "SL_Count": sl_count
    }

    summary_df = pd.read_csv(DAILY_SUMMARY_FILE)
    summary_df = summary_df[summary_df["Date"] != today]
    summary_df.loc[len(summary_df)] = summary
    summary_df.to_csv(DAILY_SUMMARY_FILE, index=False)

    # Console output (very helpful)
    print("\n📊 DAILY PERFORMANCE SUMMARY")
    print(f"Date        : {today}")
    print(f"Trades      : {trades}")
    print(f"Wins/Losses : {wins}/{losses}")
    print(f"Breakeven   : {breakeven}")
    print(f"Net PnL     : ₹{net_pnl}")
    print(f"Max Win     : ₹{max_profit}")
    print(f"Max Loss    : ₹{max_loss}")
    print(f"SL Count    : {sl_count}")
