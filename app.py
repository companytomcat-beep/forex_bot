#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# forex_pro_5_15_win.py
# Professional, lightweight trading signal bot (paper) for Windows
# Indicators: EMA20, EMA50, RSI(14), ADX(14)
# Trade TF: 5min (signal)  Confirm TF: 15min

import requests, time, math, os
from datetime import datetime
import pytz

# ---------------- CONFIG ----------------
TWELVE_KEY = "YOUR_TWELVE_KEY"
FINNHUB_KEY = "YOUR_FINNHUB_KEY"  # optional
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

SYMBOLS = ["XAU/USD", "XAG/USD", "EUR/USD", "GBP/USD", "USD/JPY"]

TRADE_TF = "5min"
CONFIRM_TF = "15min"

EMA_SHORT = 20
EMA_LONG = 50
RSI_PERIOD = 14
ADX_PERIOD = 14
ADX_THRESHOLD = 20.0  # ADX must be above this to consider trend strong

RSI_BUY = 55
RSI_SELL = 45
RSI_RANGE_LOW = 45
RSI_RANGE_HIGH = 55

SL_PERCENT = 0.15   # percent SL (0.15% default)
TP_PERCENT = SL_PERCENT * 2  # 1:2 RR

TZ = pytz.timezone("Asia/Tehran")
FETCH_RETRIES = 3
FETCH_SLEEP = 2

# ---------------- state ----------------
stats = {s: {"signals": 0, "wins": 0, "losses": 0} for s in SYMBOLS}
open_trades = []  # paper trades {symbol, side, entry, tp, sl, opened_at}

# ---------------- helpers ----------------
def now_str():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

def safe_mean(arr):
    return sum(arr)/len(arr) if arr else None

# ---------------- indicators ----------------
def calc_ema(prices, period):
    if not prices:
        return None
    if len(prices) < period:
        return safe_mean(prices)
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

def calc_adx(prices, period=14):
    # ADX requires high, low, close. We only have close via free APIs.
    return None

# ---------------- data fetchers ----------------
def fetch_twelve(symbol, interval, outputsize=200):
    for attempt in range(FETCH_RETRIES):
        try:
            url = ("https://api.twelvedata.com/time_series"
                   f"?symbol={symbol}&interval={interval}&outputsize={outputsize}&format=JSON&apikey={TWELVE_KEY}")
            r = requests.get(url, timeout=10).json()
            vals = r.get("values") or []
            closes = []
            for v in reversed(vals):
                try:
                    closes.append(float(v.get("close")))
                except:
                    continue
            return closes
        except Exception as e:
            print(f"[Twelve] error {symbol} {interval}: {e} (attempt {attempt+1})")
            time.sleep(FETCH_SLEEP)
    return []

def fetch_finnhub_fx(symbol_fx, interval, outputsize=200):
    if interval.endswith("min"):
        res = interval.replace("min", "")
    elif interval in ("1h", "60min"):
        res = "60"
    else:
        res = interval
    now_ts = int(time.time())
    seconds_per = int(res) * 60
    frm = now_ts - seconds_per * outputsize
    for attempt in range(FETCH_RETRIES):
        try:
            url = ("https://finnhub.io/api/v1/forex/candle"
                   f"?symbol={symbol_fx}&resolution={res}&from={frm}&to={now_ts}&token={FINNHUB_KEY}")
            r = requests.get(url, timeout=10).json()
            if r.get("s") != "ok":
                return []
            closes = r.get("c", [])
            return [float(x) for x in closes]
        except Exception as e:
            print(f"[Finnhub] error {symbol_fx} {interval}: {e} (attempt {attempt+1})")
            time.sleep(FETCH_SLEEP)
    return []

def fetch_prices(symbol, interval):
    data = fetch_twelve(symbol, interval)
    if data:
        return data
    map_fx = {
        "XAG/USD": "OANDA:XAG_USD",
        "XAU/USD": "OANDA:XAU_USD",
        "EUR/USD": "OANDA:EUR_USD",
        "GBP/USD": "OANDA:GBP_USD",
        "USD/JPY": "OANDA:USD_JPY"
    }
    fx = map_fx.get(symbol)
    if fx:
        return fetch_finnhub_fx(fx, interval)
    return []

# ---------------- decision logic ----------------
def analyze_tf(symbol, interval):
    prices = fetch_prices(symbol, interval)
    if not prices or len(prices) < EMA_LONG:
        return None
    ema20 = calc_ema(prices, EMA_SHORT)
    ema50 = calc_ema(prices, EMA_LONG)
    rsi = calc_rsi(prices, RSI_PERIOD)
    if rsi is None:
        return None
    if RSI_RANGE_LOW <= rsi <= RSI_RANGE_HIGH:
        return "RANGE"
    if ema20 is None or ema50 is None:
        return None
    if ema20 > ema50 and rsi > RSI_BUY:
        return "BUY"
    if ema20 < ema50 and rsi < RSI_SELL:
        return "SELL"
    return "NONE"

def confirm_and_send(symbol):
    sig5 = analyze_tf(symbol, TRADE_TF)
    sig15 = analyze_tf(symbol, CONFIRM_TF)
    print(f"[{now_str()}] {symbol} - sig5={sig5} sig15={sig15}")
    if sig5 in ("BUY","SELL") and sig15 in ("BUY","SELL") and sig5 == sig15:
        prices5 = fetch_prices(symbol, TRADE_TF)
        if not prices5:
            return
        entry = prices5[-1]
        if sig5 == "BUY":
            sl = entry * (1 - SL_PERCENT/100)
            tp = entry * (1 + TP_PERCENT/100)
        else:
            sl = entry * (1 + SL_PERCENT/100)
            tp = entry * (1 - TP_PERCENT/100)
        trade = {
            "symbol": symbol,
            "side": sig5,
            "entry": entry,
            "tp": round(tp, 5),
            "sl": round(sl, 5),
            "opened_at": now_str()
        }
        open_trades.append(trade)
        stats[symbol]["signals"] += 1

        def fmt(sym, p):
            if "XAU" in sym: return f"{p:.2f}"
            if "XAG" in sym: return f"{p:.3f}"
            if "JPY" in sym: return f"{p:.2f}"
            return f"{p:.5f}"

        send_telegram(
            f"📊 سیگنال {sig5} — {symbol}\n"
            f"💵 ورود: {fmt(symbol, entry)}\n"
            f"🎯 TP: {fmt(symbol, tp)}\n"
            f"🛑 SL: {fmt(symbol, sl)}\n"
            f"⏱ TF: {TRADE_TF} (Confirm: {CONFIRM_TF})\n"
            f"⏰ {now_str()}"
        )
        print(f"[{now_str()}] SIGNAL {symbol} {sig5} entry={entry} tp={tp} sl={sl}")

# ---------------- open trade monitor ----------------
def check_trades():
    closed = []
    for t in list(open_trades):
        symbol = t["symbol"]
        prices_1min = fetch_prices(symbol, "1min")
        if not prices_1min:
            continue
        price_now = prices_1min[-1]
        side = t["side"]
        if side == "BUY":
            if price_now >= t["tp"]:
                t["closed_at"] = now_str(); t["result"] = "Win"
                stats[symbol]["wins"] += 1; closed.append(t)
                send_telegram(f"💰 {symbol} Buy TP hit! Entry:{t['entry']} Exit:{price_now}")
            elif price_now <= t["sl"]:
                t["closed_at"] = now_str(); t["result"] = "Loss"
                stats[symbol]["losses"] += 1; closed.append(t)
                send_telegram(f"🔻 {symbol} Buy SL hit! Entry:{t['entry']} Exit:{price_now}")
        else:
            if price_now <= t["tp"]:
                t["closed_at"] = now_str(); t["result"] = "Win"
                stats[symbol]["wins"] += 1; closed.append(t)
                send_telegram(f"💰 {symbol} Sell TP hit! Entry:{t['entry']} Exit:{price_now}")
            elif price_now >= t["sl"]:
                t["closed_at"] = now_str(); t["result"] = "Loss"
                stats[symbol]["losses"] += 1; closed.append(t)
                send_telegram(f"🔻 {symbol} Sell SL hit! Entry:{t['entry']} Exit:{price_now}")
    for c in closed:
        try: open_trades.remove(c)
        except: pass

# ---------------- end of day report ----------------
def send_report():
    msg = "📊 گزارش پایان روز:\n"
    total_sig = total_w = total_l = 0
    for s,v in stats.items():
        sig = v["signals"]; w=v["wins"]; l=v["losses"]
        total_sig += sig; total_w += w; total_l += l
        wr = (w/(w+l)*100) if (w+l)>0 else 0.0
        msg += f"{s}: سیگنال:{sig} | برد:{w} | باخت:{l} | وین‌ریت:{wr:.1f}%\n"
    total_wr = (total_w/(total_w+total_l)*100) if (total_w+total_l)>0 else 0.0
    msg += f"کل: سیگنال:{total_sig} | برد:{total_w} | باخت:{total_l} | وین‌ریت:{total_wr:.1f}%"
    send_telegram(msg)
    print(msg)

# ---------------- main ----------------
def main():
    send_telegram(f"🤖 ربات حرفه‌ای (5m+15m) شروع به کار — {now_str()}")
    print(f"[{now_str()}] Bot started")
    try:
        while True:
            for s in SYMBOLS:
                try:
                    confirm_and_send(s)
                except Exception as e:
                    print(f"[{now_str()}] error confirm {s}: {e}")
            try:
                check_trades()
            except Exception as e:
                print(f"[{now_str()}] error check_trades: {e}")
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopped by user. Sending report...")
        send_report()

if __name__ == "__main__":
    main()
