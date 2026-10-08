from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from quant_logic import get_current_signal
from database import save_signal, get_signal_history

app = FastAPI()


@app.get("/signal")
def read_signal():
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
    return signal


@app.get("/history")
def read_history(limit: int = 30):
    return get_signal_history(limit)


app.mount("/", StaticFiles(directory="static", html=True), name="dashboard")