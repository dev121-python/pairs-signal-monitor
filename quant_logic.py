"""
Quant logic for the live pairs signal monitor.

These three functions (compute_hedge_ratio, compute_spread,
generate_signals) are copied unchanged from the original backtester
project (pairs-trading-backtester) — the validated logic isn't being
rewritten, just reused in a live-serving context.

get_current_signal() is new: it fetches recent real price data and
returns only the MOST RECENT day's spread, z-score, and position —
the live "current state" a dashboard would show, rather than a full
backtest over history.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import yfinance as yf

TICKER_A = "V"
TICKER_B = "MA"
WINDOW = 90       # the fold-validated window from the backtester project
ENTRY_Z = 2.0
EXIT_Z = 0.5
LOOKBACK_DAYS = 250  # enough history to compute a stable hedge ratio + z-score


def compute_hedge_ratio(price_a: pd.Series, price_b: pd.Series) -> float:
    log_a = np.log(price_a)
    log_b = sm.add_constant(np.log(price_b))
    model = sm.OLS(log_a, log_b).fit()
    return model.params.iloc[1]


def compute_spread(price_a: pd.Series, price_b: pd.Series, hedge_ratio: float) -> pd.Series:
    return np.log(price_a) - hedge_ratio * np.log(price_b)


def generate_signals(
    spread: pd.Series,
    window: int = WINDOW,
    entry_z: float = ENTRY_Z,
    exit_z: float = EXIT_Z,
) -> pd.DataFrame:
    rolling_mean = spread.rolling(window).mean()
    rolling_std = spread.rolling(window).std()
    z = (spread - rolling_mean) / rolling_std

    position = pd.Series(0, index=spread.index, dtype=int)
    current = 0
    for t in range(len(z)):
        if pd.isna(z.iloc[t]):
            position.iloc[t] = 0
            continue
        if current == 0:
            if z.iloc[t] < -entry_z:
                current = 1
            elif z.iloc[t] > entry_z:
                current = -1
        else:
            if abs(z.iloc[t]) < exit_z:
                current = 0
        position.iloc[t] = current

    return pd.DataFrame({"spread": spread, "zscore": z, "position": position})


def _fetch_recent_prices(ticker_a: str, ticker_b: str, lookback_days: int) -> pd.DataFrame:
    raw = yf.download([ticker_a, ticker_b], period=f"{lookback_days}d", auto_adjust=True, progress=False)
    prices = raw["Close"][[ticker_a, ticker_b]].dropna()
    return prices


def get_current_signal() -> dict:
    """
    Fetch recent V/MA prices, compute today's spread/z-score/signal.

    Returns a plain dict (not a DataFrame) since this is what gets
    serialized straight to JSON by the FastAPI route.
    """
    prices = _fetch_recent_prices(TICKER_A, TICKER_B, LOOKBACK_DAYS)

    hedge_ratio = compute_hedge_ratio(prices[TICKER_A], prices[TICKER_B])
    spread = compute_spread(prices[TICKER_A], prices[TICKER_B], hedge_ratio)
    signals = generate_signals(spread)

    latest = signals.iloc[-1]
    position_label = {1: "long_spread", -1: "short_spread", 0: "flat"}[int(latest["position"])]

    return {
        "ticker_a": TICKER_A,
        "ticker_b": TICKER_B,
        "as_of_date": str(signals.index[-1].date()),
        "hedge_ratio": round(float(hedge_ratio), 4),
        "spread": round(float(latest["spread"]), 6),
        "zscore": round(float(latest["zscore"]), 4),
        "position": position_label,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_current_signal(), indent=2))