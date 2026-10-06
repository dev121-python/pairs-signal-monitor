from database import save_signal
from quant_logic import get_current_signal

if __name__ == "__main__":
    signal = get_current_signal()
    row = {
        "date": signal["as_of_date"],
        "ticker_a": signal["ticker_a"],
        "ticker_b": signal["ticker_b"],
        "hedge_ratio": signal["hedge_ratio"],
        "spread": signal["spread"],
        "zscore": signal["zscore"],
        "position": signal["position"],
    }
    save_signal(row)
    print(f"Saved signal for {row['date']}: {row}")