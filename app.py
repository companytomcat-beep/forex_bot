# forex_bot_single.py

import time
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# ---------------- ENV / SETTINGS ----------------
TWELVE_KEYS = [
    os.getenv("TWELVE_DATA_KEY1"),
    os.getenv("TWELVE_DATA_KEY2"),
    os.getenv("TWELVE_DATA_KEY3")
]

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CHECK_INTERVAL = 30  # فاصله بین هر بررسی به ثانیه
TF_TREND = "1h"
TF_ENTRY = "30m"
TF_CONFIRM = "5m"

EMA_SHORT = 5
EMA_LONG = 14
RSI_PERIOD = 14
RSI_BUY = 55
RSI_SELL = 45
ADX_PERIOD = 14
ADX_THRESHOLD = 20

SYMBOLS = [
    "XAU/USD","XAG/USD","EUR/USD","GBP/USD","USD/JPY",
    "USD/CHF","AUD/USD","USD/CAD","NZD/USD","EUR/JPY"
]

# ---------------- FETCH DATA ----------------
def fetch_twelve_ohlc(symbol, interval="1min", outputsize=200, key_index=0):
    key = TWELVE_KEYS[key_index % len(TWELVE_KEYS)]
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={symbol}&interval={interval}"
        f"&outputsize={outputsize}&format=JSON&apikey={key}"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        vals = data.get("values", [])
        candles = []
        for v in reversed(vals):
            try:
                candles.append({
                    "open": float(v.get("open")),
                    "high": float(v.get("high")),
                    "low": float(v.get("low")),
                    "close": float(v.get("close")),
                    "datetime": v.get("datetime")
                })
            except:
                continue
        return candles
    except:
        return []

def get_closes_from_candles(candles):
    return [c["close"] for c in candles] if candles else []

# ---------------- INDICATORS ----------------
def calc_ema(prices, period):
    if not prices: return None
    if len(prices) < period: return sum(prices)/len(prices)
    k = 2.0 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1 - k)
    return ema

def calc_rsi(prices, period=14):
    if not prices or len(prices) < period+1: return None
    gains, losses = 0.0, 0.0
    for i in range(1,len(prices)):
        d = prices[i]-prices[i-1]
        if d>0: gains += d
        else: losses -= d
    avg_gain, avg_loss = gains/period, losses/period
    if avg_loss==0: return 100.0 if avg_gain>0 else 50.0
    rs = avg_gain/avg_loss
    return 100.0 - (100.0/(1+rs))

def calc_adx_approx(prices, period=14):
    if not prices or len(prices)<period+1: return None
    diffs = [abs(prices[i]-prices[i-1]) for i in range(1,len(prices))]
    return sum(diffs[-period:])/period

# ---------------- CANDLESTICK PATTERNS ----------------
def is_bullish_engulfing(candles):
    if not candles or len(candles)<2: return False
    prev, cur = candles[-2], candles[-1]
    if prev["close"] < prev["open"] and cur["close"] > cur["open"]:
        if cur["open"] <= prev["close"] and cur["close"] >= prev["open"]:
            return True
    return False

def is_bearish_engulfing(candles):
    if not candles or len(candles)<2: return False
    prev, cur = candles[-2], candles[-1]
    if prev["close"] > prev["open"] and cur["close"] < cur["open"]:
        if cur["open"] >= prev["close"] and cur["close"] <= prev["open"]:
            return True
    return False

def is_hammer(candles):
    if not candles: return False
    c = candles[-1]
    body = abs(c["close"]-c["open"])
    low_shadow = c["open"]-c["low"] if c["close"]>=c["open"] else c["close"]-c["low"]
    high_shadow = c["high"]-max(c["open"],c["close"])
    if body < 0.5*low_shadow and high_shadow<=body: return True
    return False

def is_shooting_star(candles):
    if not candles: return False
    c = candles[-1]
    body = abs(c["close"]-c["open"])
    high_shadow = c["high"]-max(c["open"],c["close"])
    low_shadow = min(c["open"],c["close"])-c["low"]
    if body < 0.5*high_shadow and low_shadow<=body: return True
    return False
# ---------------- TELEGRAM ----------------
def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram token or chat_id not set")
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode":"HTML"}
    try:
        r = requests.post(url, data=payload, timeout=10)
        r.raise_for_status()
        res = r.json()
        if not res.get("ok"):
            print("Telegram API not ok:", res)
            return False
        return True
    except Exception as e:
        print("Telegram send error:", e)
        return False

# ---------------- ANALYSIS ----------------
def analyze_trend(symbol):
    candles = fetch_twelve_ohlc(symbol, TF_TREND)
    closes = get_closes_from_candles(candles)
    if not closes: return None
    ema_s, ema_l = calc_ema(closes, EMA_SHORT), calc_ema(closes, EMA_LONG)
    rsi = calc_rsi(closes, RSI_PERIOD)
    adx = calc_adx_approx(closes, ADX_PERIOD)
    if adx and adx<ADX_THRESHOLD: return "RANGE"
    if ema_s and ema_l and rsi:
        if ema_s>ema_l and rsi>RSI_BUY: return "BUY"
        if ema_s<ema_l and rsi<RSI_SELL: return "SELL"
    return "RANGE"

def analyze_entry(symbol):
    candles = fetch_twelve_ohlc(symbol, TF_ENTRY)
    closes = get_closes_from_candles(candles)
    if not closes: return None
    ema_s, ema_l = calc_ema(closes, EMA_SHORT), calc_ema(closes, EMA_LONG)
    rsi = calc_rsi(closes, RSI_PERIOD)
    if ema_s and ema_l and rsi:
        if ema_s>ema_l and rsi>RSI_BUY: return "BUY"
        if ema_s<ema_l and rsi<RSI_SELL: return "SELL"
    return "RANGE"

def confirm_candle(symbol, expected_side):
    candles = fetch_twelve_ohlc(symbol, TF_CONFIRM)
    if not candles or len(candles)<1: return False
    rsi = calc_rsi(get_closes_from_candles(candles), RSI_PERIOD)
    if expected_side=="BUY":
        if is_bullish_engulfing(candles) or is_hammer(candles):
            if rsi and rsi>50: return True
    if expected_side=="SELL":
        if is_bearish_engulfing(candles) or is_shooting_star(candles):
            if rsi and rsi<50: return True
    return False

# ---------------- MAIN LOOP ----------------
def main():
    send_telegram(f"✅ ربات شروع شد و آنلاین است - TFs: {TF_TREND}/{TF_ENTRY}/{TF_CONFIRM}")
    last_alive = time.time()
    key_index = 0
    while True:
        try:
            for sym in SYMBOLS:
                trend = analyze_trend(sym)
                entry = analyze_entry(sym)
                debug_msg = f"[DEBUG] {sym}: trend={trend} entry={entry}"
                print(debug_msg)
                # تایید کندلی
                if trend in ("BUY","SELL") and entry==trend:
                    if confirm_candle(sym, trend):
                        msg = f"📈 {sym} Signal: {trend}"
                        send_telegram(msg)
                # سوئیچ API بعد هر نماد
                key_index += 1
                time.sleep(1)  # فاصله بین هر درخواست API
            # اعلام وضعیت هر نیم ساعت
            if time.time()-last_alive>1800:
                send_telegram("✅ ربات فعال است")
                last_alive = time.time()
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            err_msg = f"⚠️ ربات متوقف شد: {e}"
            send_telegram(err_msg)
            print(err_msg)
            time.sleep(30)  # فاصله قبل از تلاش مجدد

if __name__=="__main__":
    main()
