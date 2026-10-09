import sys
from database import save_signal
from quant_logic import get_current_signal

if __name__ == "__main__":
    try:
        signal = get_current_signal()
    except RuntimeError as e:
        print(f"FAILED to compute signal: {e}", file=sys.stderr)
        sys.exit(1)

    row = {
        "date": signal["as_of_date"],
        "ticker_a": signal["ticker_a"],
        "ticker_b": signal["ticker_b"],
        "hedge_ratio": signal["hedge_ratio"],
        "spread": signal["spread"],
        "zscore": signal["zscore"],
        "position": signal["position"],
    }

    try:
        save_signal(row)
    except Exception as e:
        print(f"FAILED to save signal to DB: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Saved signal for {row['date']}: {row}")