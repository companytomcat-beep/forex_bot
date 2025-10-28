# config/settings.py
import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# ----------------- API Keys -----------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWELVE_KEY = os.getenv("TWELVE_DATA_KEY")

# ----------------- Fetch & Retry -----------------
FETCH_RETRIES = 3      # تعداد تلاش برای گرفتن داده
FETCH_SLEEP = 2        # ثانیه تاخیر بین تلاش‌ها

# ----------------- Strategy -----------------
EMA_SHORT = 9
EMA_LONG = 21
RSI_PERIOD = 14
RSI_BUY = 60
RSI_SELL = 40
ADX_PERIOD = 14
ADX_THRESHOLD = 25

# ----------------- Timeframes -----------------
TF_TREND = "1h"        # جهت روند (H1 برای شما)
TF_ENTRY = "30min"     # محل ورود اولیه
TF_CONFIRM = "5min"    # تایید کندلی

# ----------------- Trading Pairs -----------------
SYMBOLS = [
    "XAU/USD","XAG/USD","EUR/USD","GBP/USD","USD/JPY",
    "BTC/USD","ETH/USD","DOGE/USD","BNB/USD"
]

