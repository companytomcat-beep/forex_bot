# core/signals.py
from core.indicators import calc_ema, calc_rsi
from config import settings

def analyze_tf(prices, ema_short=settings.EMA_SHORT, ema_long=settings.EMA_LONG,
               rsi_period=settings.RSI_PERIOD):
    """
    بررسی یک تایم‌فریم و تصمیم‌گیری سیگنال
    خروجی: "BUY", "SELL", "RANGE" یا "NONE"
    """
    if not prices or len(prices) < ema_long:
        return None

    ema20 = calc_ema(prices, ema_short)
    ema50 = calc_ema(prices, ema_long)
    rsi = calc_rsi(prices, rsi_period)

    if rsi is None:
        return None
    if settings.RSI_RANGE_LOW <= rsi <= settings.RSI_RANGE_HIGH:
        return "RANGE"
    if ema20 is None or ema50 is None:
        return None
    if ema20 > ema50 and rsi > settings.RSI_BUY:
        return "BUY"
    if ema20 < ema50 and rsi < settings.RSI_SELL:
        return "SELL"
    return "NONE"
