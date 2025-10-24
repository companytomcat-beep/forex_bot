# app.py
import time
from config import settings
from core.signals import analyze_tf
from core.trader import create_trade, check_trades, send_report, open_trades
from telegram.bot import send_telegram
import requests

# ---------------- داده‌ها ----------------
def fetch_twelve(symbol, interval, outputsize=200):
    """گرفتن قیمت‌ها از API TwelveData"""
    for attempt in range(settings.FETCH_RETRIES):
        try:
            url = ("https://api.twelvedata.com/time_series"
                   f"?symbol={symbol}&interval={interval}&outputsize={outputsize}&format=JSON&apikey={settings.TWELVE_KEY}")
            r = requests.get(url, timeout=10).json()
            vals = r.get("values") or []
            closes = [float(v.get("close")) for v in reversed(vals) if "close" in v]
            return closes
        except Exception as e:
            print(f"[Twelve] error {symbol} {interval}: {e} (attempt {attempt+1})")
            time.sleep(settings.FETCH_SLEEP)
    return []

def fetch_prices(symbol, interval):
    """قیمت‌ها را از TwelveData بگیر"""
    return fetch_twelve(symbol, interval)

# ---------------- حلقه اصلی ----------------
def main():
    send_telegram(f"🤖 ربات سیگنال‌دهنده شروع به کار — {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("[INFO] Bot started")
    try:
        while True:
            prices_now_dict = {}
            for symbol in settings.SYMBOLS:
                # دریافت قیمت‌ها
                prices_trade = fetch_prices(symbol, settings.TRADE_TF)
                prices_confirm = fetch_prices(symbol, settings.CONFIRM_TF)
                if not prices_trade or not prices_confirm:
                    continue

                # تحلیل تایم‌فریم‌ها
                sig_trade = analyze_tf(prices_trade)
                sig_confirm = analyze_tf(prices_confirm)
                print(f"[INFO] {symbol} — TF:{settings.TRADE_TF}={sig_trade} TF:{settings.CONFIRM_TF}={sig_confirm}")

                # اگر هر دو تایم‌فریم همسو بود، سیگنال بده
                if sig_trade in ("BUY","SELL") and sig_confirm in ("BUY","SELL") and sig_trade == sig_confirm:
                    entry = prices_trade[-1]
                    create_trade(symbol, sig_trade, entry)

                # ذخیره قیمت فعلی برای بررسی TP/SL
                prices_now_dict[symbol] = prices_trade[-1]

            # بررسی تریدهای باز
            check_trades(prices_now_dict)

            # هر 60 ثانیه تکرار
            time.sleep(60)

    except KeyboardInterrupt:
        print("Stopped by user. Sending report...")
        send_report()

if __name__ == "__main__":
    main()
