import ccxt
import pandas as pd
import requests
import time
import os

SYMBOL = "BTC/USDT"
TIMEFRAME = "5m"
FAST_EMA = 20
SLOW_EMA = 50

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

exchange = ccxt.binance({"enableRateLimit": True})

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def EMA(s, n):
    return s.ewm(span=n, adjust=False).mean()

def VWAP(df):
    tp = (df.high + df.low + df.close) / 3
    return (tp * df.volume).cumsum() / df.volume.cumsum()

while True:
    df = pd.DataFrame(
        exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=200),
        columns=["t","open","high","low","close","volume"]
    )

    df["ema20"] = EMA(df.close, FAST_EMA)
    df["ema50"] = EMA(df.close, SLOW_EMA)
    df["vwap"]  = VWAP(df)

    c = df.iloc[-1]

    if c.close > c.ema20 > c.ema50 and c.close > c.vwap:
        send(f"🚀 LONG {SYMBOL} @ {c.close:.2f}")

    if c.close < c.ema20 < c.ema50 and c.close < c.vwap:
        send(f"🔻 SHORT {SYMBOL} @ {c.close:.2f}")

    time.sleep(60)
