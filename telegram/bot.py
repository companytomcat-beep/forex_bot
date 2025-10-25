# telegram/bot.py
import requests
from config import settings

def send_telegram(text):
    """
    ارسال پیام ساده با HTTP API تلگرام
    chat_id: عدد یا رشته‌ای که در settings.CHAT_ID هست
    """
    if not settings.BOT_TOKEN or not settings.CHAT_ID:
        print("Telegram token or chat_id not configured in .env")
        return False

    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=payload, timeout=10)
        r.raise_for_status()
        # optional: check result
        res = r.json()
        if not res.get("ok"):
            print("Telegram API returned not ok:", res)
            return False
        return True
    except Exception as e:
        print("Telegram send error:", e)
        return False
