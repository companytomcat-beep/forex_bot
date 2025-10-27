# app.py
import time
import traceback
from datetime import datetime
import pytz

from config import settings
from core.signals import analyze_combined
from core.fetch_data import get_latest_price
from core.trader import create_trade, check_trades, send_report
from telegram.bot import send_telegram

# ---------------- helpers ----------------
def now_str():
    try:
        tz = pytz.timezone(settings.TZ)
        return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# small safe wrapper to request latest price
def get_entry_price(symbol):
    try:
        p = get_latest_price(symbol, interval=settings.TF_ENTRY)
        return p
    except Exception as e:
        print(f"[{now_str()}] error getting latest price for {symbol}: {e}")
        return None

# ---------------- main loop ----------------
def main_loop(poll_interval=60):
    send_telegram(f"🤖 ربات سیگنال‌ده (H4/H1/M30) شروع به کار — {now_str()}")
    print(f"[{now_str()}] Bot started. Symbols: {len(settings.SYMBOLS)}")
    try:
        while True:
            try:
                for symbol in settings.SYMBOLS:
                    try:
                        sig = analyze_combined(symbol)
                        print(f"[{now_str()}] {symbol} - combined_sig={sig}")
                        # Only act on clear BUY/SELL returned by analyze_combined
                        if sig in ("BUY", "SELL"):
                            entry = get_entry_price(symbol)
                            if entry:
                                create_trade(symbol, sig, entry)
                            else:
                                print(f"[{now_str()}] {symbol} - no entry price, skipping trade creation")
                        # else: NONE, RANGE, or None => do nothing
                    except Exception as e:
                        print(f"[{now_str()}] error analyzing {symbol}: {e}")
                        traceback.print_exc()
                # after scanning all symbols, check open trades using latest prices snapshot
                try:
                    # build a dict of latest prices for all symbols (using TF_ENTRY as latest)
                    prices_now = {}
                    for s in settings.SYMBOLS:
                        p = get_latest_price(s, interval="1min")  # 1min for reactive TP/SL checks
                        if p is not None:
                            prices_now[s] = p
                    if prices_now:
                        check_trades(prices_now)
                except Exception as e:
                    print(f"[{now_str()}] error in check_trades: {e}")
                    traceback.print_exc()

            except Exception as main_e:
                print(f"[{now_str()}] Unexpected error in main loop: {main_e}")
                traceback.print_exc()

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print(f"[{now_str()}] Stopped by user. Sending report...")
        try:
            send_report()
        except Exception as e:
            print(f"[{now_str()}] error sending report: {e}")
        print("Exit.")

if __name__ == "__main__":
    # poll interval in seconds — می‌تونی این مقدار رو تغییر بدی (مثلاً 60 یا 30)
    main_loop(poll_interval=60)
