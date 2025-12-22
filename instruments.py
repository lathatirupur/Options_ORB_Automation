import pandas as pd
from datetime import datetime

def load_nifty_options(kite):
    df = pd.DataFrame(kite.instruments("NFO"))
    df = df[(df["name"] == "NIFTY") & (df["segment"] == "NFO-OPT")]
    df["expiry"] = pd.to_datetime(df["expiry"])
    return df

def nearest_expiry(df):
    today = datetime.now().date()
    return min(e for e in df["expiry"].dt.date.unique() if e >= today)

def get_atm_option(df, spot, side):
    strike = round(spot / 50) * 50
    expiry = nearest_expiry(df)
    opt = df[
        (df["expiry"].dt.date == expiry) &
        (df["strike"] == strike) &
        (df["instrument_type"] == side)
    ]
    return opt.iloc[0]["tradingsymbol"]
