import sqlite3
from pathlib import Path

import random

db_path = Path(__file__).with_name("fraud_simulator.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

fraud_path = Path(__file__).with_name("Fraud-Data.db")
fraud_conn = sqlite3.connect(fraud_path)
fraud_cursor = conn.cursor()

import pandas as pd

fraud_cursor.execute(""" 
CREATE TABLE IF NOT EXISTS frauds(
        transaction_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        amount REAL,
        time INTEGER,
        time_readable TEXT,
        merchant TEXT,
        location TEXT
        )
""")

#Check if a user has an unusually large transaction
def checkAmount(id):
    total = pd.read_sql_query("SELECT SUM(amount) FROM transactions WHERE user_id = id", con=fraud_conn)
    count = pd.read_sql_query("SELECT COUNT(*) FROM transactions WHERE user_id = id", con=fraud_conn)
    average = (total/count)
    fraudCheckNum = average * 2.5
    myFrauds = pd.read_sql_query("SELECT * FROM transaction WHERE user_id = id AND amount > fraudCheckNum")
    rows = myFrauds[["transaction_id","user_id","amount","time","time_readable","merchant","location"]].to_records(index=False)
    fraud_cursor.executemany(
        """
        INSERT INTO frauds(transaction_id, user_id, amount, time, time_readable, merchant, location)
        VALUES (?,?,?,?,?,?,?)
        """,
        rows,
    )
fraud_conn.commit()

#Main function used to detect frauds

def fraudDetector(id):
    checkAmount(id)

fraudDetector(1)
df = pd.read_sql_query("SELECT * FROM frauds WHERE amount > 40", con=fraud_conn)
print(df)
