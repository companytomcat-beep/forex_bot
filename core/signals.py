# core/signals.py
"""
تنظیمات منطق تصمیم‌گیری چندتایم‌فریمی برای ربات:
- Trend: H1  (settings.TF_TREND)
- Entry: M30  (settings.TF_ENTRY)
- Confirm: M5 (settings.TF_CONFIRM)

الگوهای کندلی: تک‌کندلی (Hammer, Shooting Star, Engulfing, Doji, Tweezer)
و سه‌کندلی (Morning Star, Evening Star, Piercing / Dark Cloud)
تشخیص‌ها با قواعد ساده و محافظه‌کار پیاده‌سازی شده‌اند.
"""
from core.fetch_data import fetch_twelve_ohlc, get_closes_from_candles, get_latest_price
from core.indicators import (
    calc_ema, calc_rsi, calc_adx_approx,
    is_bullish_engulfing, is_bearish_engulfing,
    is_hammer, is_inverted_hammer, is_shooting_star, is_hanging_man
)
from config import settings

# ---------------- helper pattern detectors (simple, conservative) ----------------

def is_doji(c):
    """کندل Doji: بدنه خیلی کوچک نسبت به کل فاصله high-low"""
    body = abs(c["close"] - c["open"])
    rng = c["high"] - c["low"]
    if rng == 0:
        return False
    return body <= 0.1 * rng  # body <= 10% of range

def is_tweezer_bottom(c_prev, c_cur):
    """Tweezer Bottom: دو کندل با لولوی پایین مشابه و کندل دوم صعودی"""
    if not c_prev or not c_cur:
        return False
    same_low = abs(c_prev["low"] - c_cur["low"]) <= 1e-8 or abs((c_prev["low"] - c_cur["low"]) / max(c_prev["low"], c_cur["low"])) < 0.0005
    return same_low and (c_cur["close"] > c_cur["open"]) and (c_prev["close"] < c_prev["open"])

def is_tweezer_top(c_prev, c_cur):
    if not c_prev or not c_cur:
        return False
    same_high = abs(c_prev["high"] - c_cur["high"]) <= 1e-8 or abs((c_prev["high"] - c_cur["high"]) / max(c_prev["high"], c_cur["high"])) < 0.0005
    return same_high and (c_cur["close"] < c_cur["open"]) and (c_prev["close"] > c_prev["open"])

def is_morning_star(candles):
    """
    ساده‌شده Morning Star:
    کندل 3 تایی: 1) نزولی با بدنه بزرگ
                 2) کندل کوچک (بدنه کوچک یا Doji)
                 3) صعودی که حداقل نیمه بدنه کندل 1 را پوشش دهد (piercing)
    """
    if not candles or len(candles) < 3:
        return False
    a, b, c = candles[-3], candles[-2], candles[-1]
    body_a = abs(a["close"] - a["open"])
    body_b = abs(b["close"] - b["open"])
    body_c = abs(c["close"] - c["open"])
    if not (a["close"] < a["open"]):  # first bearish
        return False
    if not (c["close"] > c["open"]):  # last bullish
        return False
    if body_b > 0.5 * body_a:  # middle should be relatively small (star)
        return False
    # check c closes into at least 50% of body_a
    mid_a = (a["open"] + a["close"]) / 2.0
    return c["close"] >= mid_a

def is_evening_star(candles):
    if not candles or len(candles) < 3:
        return False
    a, b, c = candles[-3], candles[-2], candles[-1]
    body_a = abs(a["close"] - a["open"])
    body_b = abs(b["close"] - b["open"])
    body_c = abs(c["close"] - c["open"])
    if not (a["close"] > a["open"]):  # first bullish
        return False
    if not (c["close"] < c["open"]):  # last bearish
        return False
    if body_b > 0.5 * body_a:
        return False
    mid_a = (a["open"] + a["close"]) / 2.0
    return c["close"] <= mid_a

def is_piercing_line(candles):
    """
    Piercing Line (bullish) - دو کندل:
    1) کندل اول bearish
    2) کندل دوم bullish که حداقل بیش از 50% بدنه کندل اول رو برمی‌گرداند
    """
    if not candles or len(candles) < 2:
        return False
    prev, cur = candles[-2], candles[-1]
    if not (prev["close"] < prev["open"] and cur["close"] > cur["open"]):
        return False
    body_prev = abs(prev["open"] - prev["close"])
    # cur close should be at least prev_close + 50% of body_prev
    return cur["close"] >= (prev["close"] + 0.5 * body_prev)

def is_dark_cloud_cover(candles):
    """Dark Cloud Cover (bearish) - mirror of Piercing"""
    if not candles or len(candles) < 2:
        return False
    prev, cur = candles[-2], candles[-1]
    if not (prev["close"] > prev["open"] and cur["close"] < cur["open"]):
        return False
    body_prev = abs(prev["open"] - prev["close"])
    return cur["close"] <= (prev["close"] - 0.5 * body_prev)

# ---------------- analysis functions ----------------

def analyze_trend_h1(symbol):
    """H1 trend analysis -> 'BUY' | 'SELL' | 'RANGE' | None"""
    candles = fetch_twelve_ohlc(symbol, settings.TF_TREND, outputsize=max(settings.EMA_LONG + 20, settings.RSI_PERIOD + 20))
    if not candles:
        return None
    closes = get_closes_from_candles(candles)
    ema_short = calc_ema(closes, settings.EMA_SHORT)
    ema_long = calc_ema(closes, settings.EMA_LONG)
    rsi = calc_rsi(closes, settings.RSI_PERIOD)
    adx = calc_adx_approx(closes, settings.ADX_PERIOD)
    if adx is not None and adx < settings.ADX_THRESHOLD:
        return "RANGE"
    if ema_short is None or ema_long is None or rsi is None:
        return None
    if ema_short > ema_long and rsi > settings.RSI_BUY:
        return "BUY"
    if ema_short < ema_long and rsi < settings.RSI_SELL:
        return "SELL"
    return "RANGE"

def analyze_entry_m30(symbol):
    """M30 entry analysis -> 'BUY'|'SELL'|'RANGE'|None"""
    candles = fetch_twelve_ohlc(symbol, settings.TF_ENTRY, outputsize=max(settings.EMA_LONG + 20, settings.RSI_PERIOD + 20))
    if not candles:
        return None
    closes = get_closes_from_candles(candles)
    ema_short = calc_ema(closes, settings.EMA_SHORT)
    ema_long = calc_ema(closes, settings.EMA_LONG)
    rsi = calc_rsi(closes, settings.RSI_PERIOD)
    # basic guards
    if ema_short is None or ema_long is None or rsi is None:
        return None
    if ema_short > ema_long and rsi > settings.RSI_BUY:
        return "BUY"
    if ema_short < ema_long and rsi < settings.RSI_SELL:
        return "SELL"
    return "RANGE"

def confirm_m5_candle(symbol, expected_side):
    """
    Confirm on M5 using:
    - single-candle patterns (Engulfing, Hammer, Inverted Hammer, Shooting Star, Hanging Man, Doji+reject)
    - two-candle patterns (Tweezer)
    - three-candle patterns (Morning/Evening Star)
    - additional Piercing / Dark Cloud
    Also require mild RSI agreement (rsi>50 for buy, <50 for sell)
    """
    candles = fetch_twelve_ohlc(symbol, settings.TF_CONFIRM, outputsize=6)
    if not candles or len(candles) < 2:
        return False
    closes = get_closes_from_candles(candles)
    rsi = calc_rsi(closes, settings.RSI_PERIOD)

    # helpers for last and prev
    last = candles[-1]
    prev = candles[-2]
    last2 = candles[-3] if len(candles) >= 3 else None

    bullish_conditions = []
    bearish_conditions = []

    # single-candle strong patterns
    if is_bullish_engulfing(candles):
        bullish_conditions.append("engulf")
    if is_bearish_engulfing(candles):
        bearish_conditions.append("engulf")
    if is_hammer(candles) or (is_doji(last) and last["close"] > last["open"]):
        bullish_conditions.append("hammer/doji")
    if is_inverted_hammer(candles):
        bullish_conditions.append("inv_hammer")
    if is_shooting_star(candles):
        bearish_conditions.append("shooting")
    if is_hanging_man(candles):
        bearish_conditions.append("hanging")

    # two-candle (tweezer)
    if is_tweezer_bottom(prev, last):
        bullish_conditions.append("tweezer_bottom")
    if is_tweezer_top(prev, last):
        bearish_conditions.append("tweezer_top")

    # three-candle
    if is_morning_star(candles):
        bullish_conditions.append("morning_star")
    if is_evening_star(candles):
        bearish_conditions.append("evening_star")

    # piercing / dark cloud
    if is_piercing_line(candles):
        bullish_conditions.append("piercing")
    if is_dark_cloud_cover(candles):
        bearish_conditions.append("darkcloud")

    # final decision with RSI agreement
    if expected_side == "BUY":
        if bullish_conditions and rsi is not None and rsi > 50:
            # optional: could require at least one strong pattern or multiple weak patterns
            return True
    elif expected_side == "SELL":
        if bearish_conditions and rsi is not None and rsi < 50:
            return True
    return False

def analyze_combined(symbol):
    """
    Full logic:
    1) H1 -> trend
    2) M30 -> entry
    3) if trend == entry == side --> check M5 confirm patterns
    returns: 'BUY'|'SELL'|'NONE'|'RANGE'|None
    """
    trend = analyze_trend_h1(symbol)
    entry = analyze_entry_m30(symbol)
    print(f"[ANALYZE] {symbol} -> H1:{trend} M30:{entry}")
    if trend is None or entry is None:
        return None
    if trend in ("BUY", "SELL") and entry == trend:
        ok = confirm_m5_candle(symbol, trend)
        if ok:
            return trend
        else:
            return "NONE"
    return "RANGE"
def analyze_signals(symbol):
    """رابط استاندارد تحلیل که الان از analyze_combined استفاده می‌کند"""
    return analyze_combined(symbol)
