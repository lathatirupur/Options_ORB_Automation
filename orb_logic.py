from datetime import datetime
import time
import pandas as pd

hold_start = None
five_min_volumes = []
bucket_start = None
bucket_volume = 0

def compute_orb(kite, token):
    today = datetime.now().date()
    from_dt = datetime.combine(today, datetime.min.time()).replace(hour=9, minute=15)
    to_dt = datetime.combine(today, datetime.min.time()).replace(hour=9, minute=30)

    candles = kite.historical_data(token, from_dt, to_dt, "5minute")
    df = pd.DataFrame(candles)
    return df["high"].max(), df["low"].min()

def check_hold(price, level, seconds, direction):
    global hold_start
    valid = price > level if direction == "CE" else price < level
    if valid:
        if not hold_start:
            hold_start = time.time()
        elif time.time() - hold_start >= seconds:
            return True
    else:
        hold_start = None
    return False

def update_volume(tick):
    global bucket_start, bucket_volume, five_min_volumes
    now = datetime.now()

    if bucket_start is None:
        bucket_start = now

    if (now - bucket_start).seconds >= 300:
        five_min_volumes.append(bucket_volume)
        bucket_volume = 0
        bucket_start = now

    bucket_volume += tick.get("volume_traded", 0)

def volume_ok(multiplier):
    if len(five_min_volumes) < 2:
        return True
    avg_vol = sum(five_min_volumes[:-1]) / max(1, len(five_min_volumes) - 1)
    return five_min_volumes[-1] >= multiplier * avg_vol
