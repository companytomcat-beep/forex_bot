# core/signals.py
from core.fetch_data import fetch_twelve_ohlc, get_closes_from_candles, get_latest_price
from core.indicators import (
    calc_ema, calc_rsi, calc_adx_approx,
    is_bullish_engulfing, is_bearish_engulfing,
    is_hammer, is_inverted_hammer, is_shooting_star, is_hanging_man,
    is_doji, is_tweezer_bottom, is_tweezer_top, is_morning_star, is_evening_star,
    is_piercing_line, is_dark_cloud_cover
)
from config import settings

def analyze_trend_h1(symbol):
    candles = fetch_twelve_ohlc(symbol, settings.TF_TREND, outputsize=max(settings.EMA_LONG+50, settings.RSI_PERIOD+50))
    if not candles:
        return None
    closes = get_closes_from_candles(candles)
    ema_s = calc_ema(closes, settings.EMA_SHORT)
    ema_l = calc_ema(closes, settings.EMA_LONG)
    rsi = calc_rsi(closes, settings.RSI_PERIOD)
    adx = calc_adx_approx(closes, settings.ADX_PERIOD)
    if adx is not None and adx < settings.ADX_THRESHOLD:
        return "RANGE"
    if ema_s is None or ema_l is None or rsi is None:
        return None
    if ema_s > ema_l and rsi > settings.RSI_BUY:
        return "BUY"
    if ema_s < ema_l and rsi < settings.RSI_SELL:
        return "SELL"
    return "RANGE"

def analyze_entry_m30(symbol):
    candles = fetch_twelve_ohlc(symbol, settings.TF_ENTRY, outputsize=max(settings.EMA_LONG+30, settings.RSI_PERIOD+30))
    if not candles:
        return None
    closes = get_closes_from_candles(candles)
    ema_s = calc_ema(closes, settings.EMA_SHORT)
    ema_l = calc_ema(closes, settings.EMA_LONG)
    rsi = calc_rsi(closes, settings.RSI_PERIOD)
    if ema_s is None or ema_l is None or rsi is None:
        return None
    if ema_s > ema_l and rsi > settings.RSI_BUY:
        return "BUY"
    if ema_s < ema_l and rsi < settings.RSI_SELL:
        return "SELL"
    return "RANGE"

def confirm_m5_candle(symbol, expected_side):
    candles = fetch_twelve_ohlc(symbol, settings.TF_CONFIRM, outputsize=6)
    if not candles or len(candles) < 2:
        return False
    closes = get_closes_from_candles(candles)
    rsi = calc_rsi(closes, settings.RSI_PERIOD)
    last = candles[-1]; prev = candles[-2]; last2 = candles[-3] if len(candles)>=3 else None

    bullish = []
    bearish = []

    # single
    if is_bullish_engulfing(candles): bullish.append("engulf")
    if is_bearish_engulfing(candles): bearish.append("engulf")
    if is_hammer(candles) or (is_doji(last) and last["close"]>last["open"]): bullish.append("hammer/doji")
    if is_inverted_hammer(candles): bullish.append("inv_hammer")
    if is_shooting_star(candles): bearish.append("shooting")
    if is_hanging_man(candles): bearish.append("hanging")

    # tweezer
    if is_tweezer_bottom(prev, last): bullish.append("tweezer")
    if is_tweezer_top(prev, last): bearish.append("tweezer")

    # three-candle
    if is_morning_star(candles): bullish.append("morning")
    if is_evening_star(candles): bearish.append("evening")

    # piercing / darkcloud
    if is_piercing_line(candles): bullish.append("piercing")
    if is_dark_cloud_cover(candles): bearish.append("darkcloud")

    if expected_side == "BUY":
        if bullish and rsi is not None and rsi > 50:
            return True
    else:
        if bearish and rsi is not None and rsi < 50:
            return True
    return False

def analyze_combined(symbol):
    trend = analyze_trend_h1(symbol)
    entry = analyze_entry_m30(symbol)
    print(f"[ANALYZE] {symbol} -> H1:{trend} M30:{entry}")
    if trend is None or entry is None:
        return None
    if trend in ("BUY","SELL") and entry == trend:
        ok = confirm_m5_candle(symbol, trend)
        return trend if ok else "NONE"
    return "RANGE"

# small wrapper for compatibility
def analyze_signals(symbol):
    return analyze_combined(symbol)
