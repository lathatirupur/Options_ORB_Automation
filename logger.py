import pandas as pd
from pathlib import Path

TRADE_FILE = "paper_trades.csv"
SUMMARY_FILE = "daily_summary.csv"

def init_logs():
    if not Path(TRADE_FILE).exists():
        pd.DataFrame(columns=[
            "Date","EntryTime","ExitTime","Symbol",
            "Entry","Exit","PnL","Reason"
        ]).to_csv(TRADE_FILE, index=False)

def log_trade(row):
    df = pd.read_csv(TRADE_FILE)
    df.loc[len(df)] = row
    df.to_csv(TRADE_FILE, index=False)

def update_summary():
    df = pd.read_csv(TRADE_FILE)
    if df.empty:
        return
    summary = df.groupby("Date")["PnL"].agg(["sum","count"])
    summary.to_csv(SUMMARY_FILE)
