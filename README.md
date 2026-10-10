# Pairs Signal Monitor

A live, daily-updating statistical arbitrage signal monitor for the Visa (V) / Mastercard (MA) pair, built on top of a validated backtesting engine. Unlike the backtester, this project focuses on backend/systems engineering: a scheduled data pipeline, a persistent database, a REST API, and a live dashboard — all running unattended.

## What it does

Each trading day, an automated job:
1. Fetches recent V/MA price data
2. Computes the hedge ratio, log-price spread, and rolling z-score (same validated logic as the pairs-trading-backtester project)
3. Determines today's position signal: `long_spread`, `short_spread`, or `flat`
4. Persists the result to a PostgreSQL database
5. Serves it via a FastAPI backend and a live dashboard

## Architecture

GitHub Actions (daily cron)
&nbsp;&nbsp;&nbsp;&nbsp;│
&nbsp;&nbsp;&nbsp;&nbsp;▼
run_daily_signal.py → quant_logic.py (hedge ratio, spread, z-score, signal)
&nbsp;&nbsp;&nbsp;&nbsp;│
&nbsp;&nbsp;&nbsp;&nbsp;▼
database.py → PostgreSQL (Render)
&nbsp;&nbsp;&nbsp;&nbsp;│
&nbsp;&nbsp;&nbsp;&nbsp;▼
FastAPI (main.py) → /signal, /history endpoints
&nbsp;&nbsp;&nbsp;&nbsp;│
&nbsp;&nbsp;&nbsp;&nbsp;▼
static/index.html (dashboard: live signal card, z-score chart, history table)

## Stack

- **Python** — pandas, numpy, yfinance for data + signal computation
- **FastAPI** + **SQLAlchemy** — REST API and ORM
- **PostgreSQL** (Render) — persistent signal history
- **GitHub Actions** — scheduled daily automation (no server needed to keep it running)
- **Chart.js** — dashboard visualization

## Running locally

Install dependencies:

    pip install -r requirements.txt

Create a `.env` file with:

    DATABASE_URL=postgresql+psycopg2://user:password@host/dbname

Start the server:

    uvicorn main:app --reload

Visit `http://127.0.0.1:8000` for the dashboard, or hit `/signal` and `/history` directly.

## API

| Endpoint | Description |
|---|---|
| `GET /signal` | Computes and returns today's signal, persists it to the DB |
| `GET /history?limit=30` | Returns the most recent N saved signals |

## Automation

`.github/workflows/daily-signal.yml` runs `run_daily_signal.py` on a schedule (weekdays, after US market close), computing and saving that day's signal directly against the database — no deployed server required for this part to work.

## Status

- [x] Signal computation (hedge ratio, spread, rolling z-score)
- [x] Persistent history in PostgreSQL
- [x] REST API (FastAPI)
- [x] Live dashboard
- [x] Daily automation via GitHub Actions
- [x] Error handling for data fetch / DB failures
- [ ] Deployed publicly (Render)
- [ ] Unit tests
- [ ] Multi-pair support
- [ ] Alerting on signal change