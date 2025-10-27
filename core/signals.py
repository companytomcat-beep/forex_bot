# core/signals.py
from core.fetch_data import fetch_twelve_ohlc, get_closes_from_candles, get_latest_price
from core.indicators import calc_ema, calc_rsi, calc_adx_approx, is_bullish_engulfing, is_bearish_engulfing
from config import settings

def analyze_trend_h4(symbol):
    """
    تحلیل روند در H4:
    خروجی: 'BUY' | 'SELL' | 'RANGE' | None
    """
    # تعداد کندل کافی برای EMA200 و RSI
    needed = max(settings.EMA_LONG + 10, settings.RSI_PERIOD + 10)
    candles = fetch_twelve_ohlc(symbol, settings.TF_TREND, outputsize=needed)
    if not candles:
        return None
    closes = get_closes_from_candles(candles)
    ema_short = calc_ema(closes, settings.EMA_SHORT)
    ema_long = calc_ema(closes, settings.EMA_LONG)
    rsi = calc_rsi(closes, settings.RSI_PERIOD)
    adx = calc_adx_approx(closes, settings.ADX_PERIOD)

    # ADX filter: اگر روند ضعیفه => RANGE
    if adx is not None and adx < settings.ADX_THRESHOLD:
        return "RANGE"

    if ema_short is None or ema_long is None or rsi is None:
        return None

    if ema_short > ema_long and rsi > settings.RSI_BUY:
        return "BUY"
    if ema_short < ema_long and rsi < settings.RSI_SELL:
        return "SELL"
    return "RANGE"

def analyze_entry_h1(symbol):
    """
    تحلیل ورود در H1 (محل ورود اولیه)
    خروجی: 'BUY'|'SELL'|'RANGE'|None
    """
    needed = max(settings.EMA_LONG + 10, settings.RSI_PERIOD + 10)
    candles = fetch_twelve_ohlc(symbol, settings.TF_ENTRY, outputsize=needed)
    if not candles:
        return None
    closes = get_closes_from_candles(candles)
    ema_short = calc_ema(closes, settings.EMA_SHORT)
    ema_long = calc_ema(closes, settings.EMA_LONG)
    rsi = calc_rsi(closes, settings.RSI_PERIOD)

    if ema_short is None or ema_long is None or rsi is None:
        return None

    if ema_short > ema_long and rsi > settings.RSI_BUY:
        return "BUY"
    if ema_short < ema_long and rsi < settings.RSI_SELL:
        return "SELL"
    return "RANGE"

def confirm_m30_candle(symbol, expected_side):
    """
    تایید نهایی با کندل M30:
    ترکیبی از الگوی Engulfing و RSI موافق
    بازمی‌گرداند True اگر تایید شد، در غیر این صورت False
    """
    candles = fetch_twelve_ohlc(symbol, settings.TF_CONFIRM, outputsize=6)
    if not candles or len(candles) < 2:
        return False
    closes = get_closes_from_candles(candles)
    rsi = calc_rsi(closes, settings.RSI_PERIOD)

    if expected_side == "BUY":
        if is_bullish_engulfing(candles) and rsi is not None and rsi > 50:
            return True
    elif expected_side == "SELL":
        if is_bearish_engulfing(candles) and rsi is not None and rsi < 50:
            return True
    return False

def analyze_combined(symbol):
    """
    منطق نهایی:
    1) H4 جهت روند را مشخص می‌کند (trend)
    2) H1 محل ورود را مشخص می‌کند (entry)
    3) اگر trend و entry هم‌جهت باشند، کندل M30 را برای تایید نهایی بررسی می‌کنیم
    خروجی: 'BUY' | 'SELL' | 'NONE' | 'RANGE' | None
    """
    trend = analyze_trend_h4(symbol)
    entry = analyze_entry_h1(symbol)

    print(f"[ANALYZE] {symbol} -> H4:{trend} H1:{entry}")

    if trend is None or entry is None:
        return None

    if trend in ("BUY", "SELL") and entry == trend:
        ok = confirm_m30_candle(symbol, trend)
        if ok:
            return trend
        else:
            return "NONE"   # هم‌جهت ولی تایید M30 نگرفته
    return "RANGE"
