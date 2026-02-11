import sqlite3
from pathlib import Path

import random

db_path = Path(__file__).with_name("fraud_simulator.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

fraud_path = Path(__file__).with_name("Fraud-Data.db")
fraud_conn = sqlite3.connect(fraud_path)
fraud_cursor = fraud_conn.cursor()

import pandas as pd

#fraud_cursor.execute("DROP TABLE frauds")

fraud_cursor.execute(""" 
CREATE TABLE IF NOT EXISTS frauds(
        transaction_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        amount REAL,
        time INTEGER,
        time_readable TEXT,
        merchant TEXT,
        location TEXT,
        isFraud BOOLEAN
        )
""")

#Check if a user has an unusually large transaction
def checkAmount(id):
    total_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ?",
        con = conn,
        params=[id]

    )
    total_df_sum = pd.read_sql_query(
        "SELECT SUM(amount) FROM transactions WHERE user_id = ?",
        con=conn,
        params=[id],
    )
    count_df = pd.read_sql_query(
        "SELECT COUNT(*) FROM transactions WHERE user_id = ?",
        con=conn,
        params=[id],
    )
    total = total_df_sum.iloc[0, 0] or 0
    count = count_df.iloc[0, 0] or 0
    if count == 0:
        return
    average = total / count
    fraudCheckNum = average * 2
    rows = []
    for i in range(len(total_df)):
        current_df = total_df.iloc[i]
        if current_df["amount"] > fraudCheckNum:
            rows.append(
                (
                    int(current_df["transaction_id"]),
                    int(current_df["user_id"]),
                    float(current_df["amount"]),
                    int(current_df["time"]),
                    str(current_df["time_readable"]),
                    str(current_df["merchant"]),
                    str(current_df["location"]),
                    True,
                )
            )
    if rows:
        fraud_cursor.executemany(
            """
            INSERT INTO frauds(
                transaction_id,
                user_id,
                amount,
                time,
                time_readable,
                merchant,
                location,
                isFraud
            )
            VALUES (?,?,?,?,?,?,?,?)
            """,
            rows
        )
        fraud_conn.commit()


#Checks if user has two transactions that occur in 2 far away places in too short of a timeframe
def checkLocation(id):
    total_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY time",
        con=conn,
        params=[id]
    )
    rows = [[]]
    for i in range(len(total_df) - 1):
        current_df = total_df.iloc[i]
        next_df = total_df.iloc[i + 1]
        if current_df["location"] != next_df["location"]:
            difference = next_df["time"] - current_df["time"]
            if difference <= 600:
                rows.append(
                    (
                        int(current_df["transaction_id"]),
                        int(current_df["user_id"]),
                        float(current_df["amount"]),
                        int(current_df["time"]),
                        str(current_df["time_readable"]),
                        str(current_df["merchant"]),
                        str(current_df["location"]),
                        True,
                    )
                )
                rows.append(
                    (
                        int(next_df["transaction_id"]),
                        int(next_df["user_id"]),
                        float(next_df["amount"]),
                        int(next_df["time"]),
                        str(next_df["time_readable"]),
                        str(next_df["merchant"]),
                        str(next_df["location"]),
                        True,
                    )
                )
    if rows:
        fraud_cursor.executemany(
            """
            INSERT OR IGNORE INTO frauds(
                transaction_id,
                user_id,
                amount,
                time,
                time_readable,
                merchant,
                location,
                isFraud
            )
            VALUES (?,?,?,?,?,?,?,?)
            """,
            rows
        )
    fraud_conn.commit()
                

                
#Main function used to detect frauds
def fraudDetector(id):
    checkAmount(id)
    checkLocation(id)

fraud_conn.commit()

fraudDetector(2)
df = pd.read_sql_query("SELECT * FROM frauds", con=fraud_conn)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
print(df)
