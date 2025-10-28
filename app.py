# app.py
from core.fetch_data import fetch_twelve_ohlc, get_latest_price
from core.signals import analyze_signals
from core.pairs import PAIRS
from telegram.bot import send_telegram
import time

def main():
    send_telegram("✅ ربات شروع شد و آنلاین است")
    while True:
        for symbol in PAIRS:
            candles = fetch_twelve_ohlc(symbol, interval="1h", outputsize=200)
            if not candles:
                continue
            signal = analyze_signals(symbol, candles)
            if signal:
                send_telegram(f"📊 سیگنال برای {symbol}: {signal}")
        time.sleep(60)

if __name__ == "__main__":
    main()
