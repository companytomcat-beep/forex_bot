# telegram/bot.py
import requests
from config import settings

def send_telegram(text):
    """
    Send a simple message to Telegram using HTTP API.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        print("[TELEGRAM] token or chat_id not configured")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=payload, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            print("[TELEGRAM] API returned not ok:", data)
            return False
        return True
    except Exception as e:
        print("[TELEGRAM] send error:", e)
        return False
