"""One-off: rebuild past daily signals using the same logic as the live monitor."""
import pandas as pd
import yfinance as yf

from quant_logic import (
    TICKER_A, TICKER_B, WINDOW, LOOKBACK_DAYS,
    compute_hedge_ratio, compute_spread, generate_signals,
)
from database import save_signal

START = "2026-10-08"   # first day to rebuild; change if you want

raw = yf.download(
    [TICKER_A, TICKER_B],
    start=pd.Timestamp(START) - pd.Timedelta(days=LOOKBACK_DAYS + 30),
    auto_adjust=True, progress=False, threads=False,
)
prices = raw["Close"][[TICKER_A, TICKER_B]].dropna()

labels = {1: "long_spread", -1: "short_spread", 0: "flat"}
saved = 0
for day in prices.index[prices.index >= START]:
    window = prices.loc[day - pd.Timedelta(days=LOOKBACK_DAYS): day]
    if len(window) < WINDOW:
        continue
    hedge = compute_hedge_ratio(window[TICKER_A], window[TICKER_B])
    spread = compute_spread(window[TICKER_A], window[TICKER_B], hedge)
    latest = generate_signals(spread).iloc[-1]
    if pd.isna(latest["zscore"]):
        continue
    save_signal({
        "date": str(day.date()),
        "ticker_a": TICKER_A,
        "ticker_b": TICKER_B,
        "hedge_ratio": round(float(hedge), 4),
        "spread": round(float(latest["spread"]), 6),
        "zscore": round(float(latest["zscore"]), 4),
        "position": labels[int(latest["position"])],
    })
    saved += 1

print(f"Saved {saved} days")