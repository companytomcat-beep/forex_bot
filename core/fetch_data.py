# core/fetch_data.py
import time, requests
from config import settings

def fetch_twelve_ohlc(symbol, interval="1min", outputsize=500):
    """
    Return list of candles dicts [{'open','high','low','close','datetime'}, ...]
    Order: oldest ... newest (index -1 is latest)
    """
    api_key = settings.TWELVE_KEY
    if not api_key:
        print("[FETCH] TwelveData API key not configured")
        return []
    for attempt in range(settings.FETCH_RETRIES):
        try:
            url = (
                f"https://api.twelvedata.com/time_series"
                f"?symbol={symbol}&interval={interval}&outputsize={outputsize}&format=JSON&apikey={api_key}"
            )
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            vals = data.get("values") or []
            candles = []
            for v in reversed(vals):  # Twelve returns newest->oldest, reverse it
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
            print(f"[FETCH] Twelve error {symbol} {interval}: {e} (attempt {attempt+1})")
            time.sleep(settings.FETCH_SLEEP)
    return []

def get_closes_from_candles(candles):
    return [c["close"] for c in candles] if candles else []

def get_latest_price(symbol, interval="1min"):
    c = fetch_twelve_ohlc(symbol, interval=interval, outputsize=2)
    if c:
        return c[-1]["close"]
    return None
