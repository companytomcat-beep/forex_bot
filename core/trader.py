# core/trader.py
from utils.helpers import now_str
from config import settings
from telegram.bot import send_telegram

# نگهداری تریدهای باز (Paper Trades)
open_trades = []
stats = {s: {"signals": 0, "wins": 0, "losses": 0} for s in settings.SYMBOLS}

def create_trade(symbol, side, entry):
    """ایجاد یک ترید جدید با محاسبه TP و SL"""
    if side == "BUY":
        sl = entry * (1 - settings.SL_PERCENT/100)
        tp = entry * (1 + settings.TP_PERCENT/100)
    else:
        sl = entry * (1 + settings.SL_PERCENT/100)
        tp = entry * (1 - settings.TP_PERCENT/100)

    trade = {
        "symbol": symbol,
        "side": side,
        "entry": entry,
        "tp": round(tp, 5),
        "sl": round(sl, 5),
        "opened_at": now_str()
    }
    open_trades.append(trade)
    stats[symbol]["signals"] += 1

    # ارسال پیام به تلگرام
    send_telegram(
        f"📊 سیگنال {side} — {symbol}\n"
        f"💵 ورود: {entry}\n"
        f"🎯 TP: {round(tp,5)}\n"
        f"🛑 SL: {round(sl,5)}\n"
        f"⏱ TF: {settings.TRADE_TF} (Confirm: {settings.CONFIRM_TF})\n"
        f"⏰ {now_str()}"
    )
    print(f"[{now_str()}] SIGNAL {symbol} {side} entry={entry} tp={tp} sl={sl}")

def check_trades(prices_now_dict):
    """
    بررسی تریدهای باز و بستن آن‌ها در صورت رسیدن به TP یا SL
    prices_now_dict: {"XAU/USD": 1965.23, ...}
    """
    closed = []
    for t in list(open_trades):
        symbol = t["symbol"]
        price_now = prices_now_dict.get(symbol)
        if price_now is None:
            continue
        side = t["side"]
        if side == "BUY":
            if price_now >= t["tp"]:
                t["closed_at"] = now_str(); t["result"] = "Win"
                stats[symbol]["wins"] += 1; closed.append(t)
                send_telegram(f"💰 {symbol} Buy TP hit! Entry:{t['entry']} Exit:{price_now}")
            elif price_now <= t["sl"]:
                t["closed_at"] = now_str(); t["result"] = "Loss"
                stats[symbol]["losses"] += 1; closed.append(t)
                send_telegram(f"🔻 {symbol} Buy SL hit! Entry:{t['entry']} Exit:{price_now}")
        else:  # SELL
            if price_now <= t["tp"]:
                t["closed_at"] = now_str(); t["result"] = "Win"
                stats[symbol]["wins"] += 1; closed.append(t)
                send_telegram(f"💰 {symbol} Sell TP hit! Entry:{t['entry']} Exit:{price_now}")
            elif price_now >= t["sl"]:
                t["closed_at"] = now_str(); t["result"] = "Loss"
                stats[symbol]["losses"] += 1; closed.append(t)
                send_telegram(f"🔻 {symbol} Sell SL hit! Entry:{t['entry']} Exit:{price_now}")

    # حذف تریدهای بسته شده
    for c in closed:
        try: open_trades.remove(c)
        except: pass

def send_report():
    """گزارش روزانه از سیگنال‌ها و وین‌ریت"""
    msg = "📊 گزارش پایان روز:\n"
    total_sig = total_w = total_l = 0
    for s,v in stats.items():
        sig = v["signals"]; w=v["wins"]; l=v["losses"]
        total_sig += sig; total_w += w; total_l += l
        wr = (w/(w+l)*100) if (w+l)>0 else 0.0
        msg += f"{s}: سیگنال:{sig} | برد:{w} | باخت:{l} | وین‌ریت:{wr:.1f}%\n"
    total_wr = (total_w/(total_w+total_l)*100) if (total_w+total_l)>0 else 0.0
    msg += f"کل: سیگنال:{total_sig} | برد:{total_w} | باخت:{total_l} | وین‌ریت:{total_wr:.1f}%"
    send_telegram(msg)
    print(msg)
