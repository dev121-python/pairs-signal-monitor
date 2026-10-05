from fastapi import FastAPI
from quant_logic import get_current_signal

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, world"}  # keep whatever your existing / route does


@app.get("/signal")
def read_signal():
    return get_current_signal()