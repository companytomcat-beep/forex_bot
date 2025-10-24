# utils/helpers.py
from datetime import datetime
import pytz

def now_str(timezone="Asia/Tehran"):
    tz = pytz.timezone(timezone)
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def safe_mean(arr):
    return sum(arr)/len(arr) if arr else None
