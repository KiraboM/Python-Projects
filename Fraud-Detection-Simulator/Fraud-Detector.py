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
    for i in range (len(total_df)):
        current_df = total_df[i]
        if(current_df["amount"] > fraudCheckNum):
            current_df["isFraud"] = True#Mark transactions that are abnormally large as fraud


#Checks if user has two transactions that occur in 2 far away places in too short of a timeframe
def checkLocation(id):
    total_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY time",
        con=conn,
        params=[id]
    )
    for i in range (len(total_df) - 1):
        current_df = total_df.iloc[i]
        next_df = total_df.iloc[i + 1]
        if(current_df["location"] == next_df["location"]):
            difference = next_df["time"] - current_df["time"]
            if(difference <= 600):
                current_df["isFraud"] = True
                next_df["isFraud"] = True

                
#Main function used to detect frauds
fraud_cursor.execute("DELETE FROM frauds")
fraud_conn.commit()
def fraudDetector(id):
    checkAmount(id)
    checkLocation(id)
    frauds_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE isFraud = ?",
        con=conn,
        params=[True]
    )
     rows = list(
        frauds_df[
            [
                "transaction_id",
                "user_id",
                "amount",
                "time",
                "time_readable",
                "merchant",
                "location",
                "isFraud",
            ]
        ].itertuples(index=False, name=None)
    if rows:
        fraud_cursor.execute(
            """
            INSERT INTO frauds(transaction_id, user_id, amount, time, time_readable, merchant, location)
            VALUES (?,?,?,?,?,?,?)
            """,
            rows,
        )
fraud_conn.commit()

fraudDetector(2)
df = pd.read_sql_query("SELECT * FROM frauds", con=fraud_conn)
print(df)
