
import csv
import logging
import os
import sqlite3
from dotenv import load_dotenv

# PIECE 1: read the settings from the .env file
load_dotenv()
db_name = os.getenv("DB_NAME")
csv_path = os.getenv("CSV_PATH")
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

# PIECE 2: create the database and the table
conn = sqlite3.connect(db_name)

conn.execute("""
CREATE TABLE IF NOT EXISTS sales (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT,
    amount REAL,
    category TEXT
)
""")

# PIECE 3: read the CSV, skip bad rows, save good rows
good_count = 0

with open(csv_path, newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        # Is anything empty? Then skip this row.
        if (not row["transaction_id"] or not row["customer_id"]
                or not row["amount"] or not row["category"]):
            logging.warning("Skipping row %s: missing data", row["transaction_id"])
            continue

        # The ? marks are safe blanks that get filled in by the database
        conn.execute(
            "INSERT OR REPLACE INTO sales (transaction_id, customer_id, amount, category) "
            "VALUES (?, ?, ?, ?)",
            (row["transaction_id"], row["customer_id"], float(row["amount"]), row["category"]),
        )
        good_count = good_count + 1

conn.commit()
logging.info("Rows saved: %d", good_count)

# PIECE 4: show what is in the database
print("--- Rows in the sales table ---")
rows = conn.execute("SELECT * FROM sales").fetchall()
for r in rows:
    print(r)

conn.close()