from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from quant_logic import get_current_signal
from database import save_signal, get_signal_history

app = FastAPI()


@app.get("/signal")
def read_signal():
    try:
        signal = get_current_signal()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

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
    except Exception:
        # Signal was computed fine, just couldn't persist it — still return it
        pass

    return signal


@app.get("/history")
def read_history(limit: int = 30):
    return get_signal_history(limit)


app.mount("/", StaticFiles(directory="static", html=True), name="dashboard")