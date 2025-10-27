# core/fetch_data.py
import time
import requests
from config import settings

def fetch_twelve_ohlc(symbol, interval="1min", outputsize=200):
    """
    برگشت لیست کندل‌ها به شکل [{'open':..,'high':..,'low':..,'close':.., 'datetime':..}, ...]
    ترتیب: از قدیم به جدید (index 0 قدیمی‌ترین)
    """
    for attempt in range(settings.FETCH_RETRIES):
        try:
            url = (
                f"https://api.twelvedata.com/time_series"
                f"?symbol={symbol}&interval={interval}"
                f"&outputsize={outputsize}&format=JSON&apikey={settings.TWELVE_KEY}"
            )
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            vals = data.get("values", [])  # TwelveData برمی‌گردونه از جدید به قدیم
            candles = []
            # معکوس می‌کنیم تا ترتیب از قدیم به جدید باشه
            for v in reversed(vals):
                try:
                    candles.append({
                        "open": float(v.get("open")),
                        "high": float(v.get("high")),
                        "low": float(v.get("low")),
                        "close": float(v.get("close")),
                        "datetime": v.get("datetime")
                    })
                except Exception:
                    continue
            return candles
        except Exception as e:
            print(f"[Twelve] error {symbol} {interval}: {e} (attempt {attempt+1})")
            time.sleep(settings.FETCH_SLEEP)
    return []

def get_closes_from_candles(candles):
    return [c["close"] for c in candles] if candles else []

def get_latest_price(symbol, interval="1min"):
    candles = fetch_twelve_ohlc(symbol, interval, outputsize=2)
    if candles:
        return candles[-1]["close"]
    return None
