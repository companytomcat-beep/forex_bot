# telegram/bot.py
import requests
from config import settings

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": settings.CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)
