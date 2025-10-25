# core/fetch_data.py
import requests
import time
from config import settings

def fetch_twelve(symbol, interval="1min", outputsize=200):
    for attempt in range(settings.FETCH_RETRIES):
        try:
            url = (
                f"https://api.twelvedata.com/time_series"
                f"?symbol={symbol}&interval={interval}"
                f"&outputsize={outputsize}&format=JSON&apikey={settings.TWELVE_KEY}"
            )
            r = requests.get(url, timeout=10).json()
            vals = r.get("values", [])
            closes = []
            for v in reversed(vals):
                try:
                    closes.append(float(v.get("close")))
                except:
                    continue
            return closes
        except Exception as e:
            print(f"[Twelve] error {symbol} {interval}: {e} (attempt {attempt+1})")
            time.sleep(settings.FETCH_SLEEP)
    return []

def get_latest_price(symbol, interval="1min"):
    prices = fetch_twelve(symbol, interval, outputsize=1)
    if prices:
        return prices[-1]
    return None

def calc_ema(prices, period):
    if not prices:
        return None
    if len(prices) < period:
        return sum(prices)/len(prices)
    k = 2.0 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1 - k)
    return ema

def calc_rsi(prices, period=14):
    if not prices or len(prices) < period + 1:
        return None
    gains = 0.0
    losses = 0.0
    for i in range(1, len(prices)):
        d = prices[i] - prices[i-1]
        if d > 0:
            gains += d
        else:
            losses -= d
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))
