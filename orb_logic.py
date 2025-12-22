import time

hold_start = None

def check_hold(price, level, seconds):
    global hold_start
    if price > level:
        if not hold_start:
            hold_start = time.time()
        elif time.time() - hold_start >= seconds:
            return True
    else:
        hold_start = None
    return False
