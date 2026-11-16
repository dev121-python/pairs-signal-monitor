import csv
from database import get_signal_history

rows = get_signal_history(limit=100000)
rows.sort(key=lambda r: r["date"])

if rows:
    with open("signal_history.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)