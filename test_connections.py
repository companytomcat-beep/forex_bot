# test_connections.py
from config import settings
from core.fetch_data import fetch_twelve, get_latest_price
from telegram.bot import send_telegram

# ---------- تست TwelveData ----------
print("🔹 Testing TwelveData API...")
for symbol in settings.SYMBOLS[:3]:  # فقط سه نماد اول برای سرعت
    prices = fetch_twelve(symbol, interval="1min", outputsize=5)
    if prices:
        print(f"{symbol} -> OK, last prices: {prices[-3:]}")
    else:
        print(f"{symbol} -> FAILED, no data received")

# ---------- تست آخرین قیمت ----------
print("🔹 Testing get_latest_price()...")
for symbol in settings.SYMBOLS[:3]:
    latest = get_latest_price(symbol, interval="1min")
    print(f"{symbol} latest price:", latest if latest else "FAILED")

# ---------- تست Telegram ----------
print("🔹 Testing Telegram send...")
ok = send_telegram("✅ تست اتصال ربات — پیام توسط ربات ارسال شد.")
print("Telegram send:", "OK" if ok else "FAILED")
