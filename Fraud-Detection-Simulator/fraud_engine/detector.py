import sqlite3
from pathlib import Path

import random
import numpy as np



import pandas as pd

#Check if a user has an unusually large transaction
def checkAmount(id, total_df, conn):
    amounts = total_df["amount"]
    #Get mean and standard deviation from data
    average = np.mean(amounts)
    std = np.std(amounts)
    fraudCheckNum = average + 2*std

    total_df.loc[total_df["amount"] > fraudCheckNum, "fraud_score"] += 40

#Checks if user has two transactions that occur in 2 far away places in too short of a timeframe
def checkLocation(id, total_df, conn):
    cursor = conn.cursor()
    total_df = total_df.sort_values("time")
    flagged_ids = set()
    for i in range(len(total_df) - 1):
        current_df = total_df.iloc[i]
        current_id = int(current_df["transaction_id"])
        next_df = total_df.iloc[i + 1]
        next_id = int(next_df["transaction_id"])
        if current_df["location"] != next_df["location"]:
            difference = int(next_df["time"]) - int(current_df["time"])
            if difference <= 600:
                flagged_ids.add(current_id)
                flagged_ids.add(next_id)
    #Increase fraud score of all suspicious transactions
    cursor.executemany(
        "UPDATE transactions SET fraud_score = fraud_score + 40 WHERE transaction_id = ?",
        [(myID, ) for myID in flagged_ids]
    )
    conn.commit()
#If a user makes more than 10 transactions in 5 minutes 
#AND more than 3 of these transactions are to different merchants, that is suspicious!
def transactionNum(id, total_df, conn):
    cursor = conn.cursor()
    flagged_ids = set()
    #Collect every transaction of given user
    rows = []
    merchants = []
    if(len(total_df) <= 1):#Check if table has more than one element
        return
    time = 0
    left = 0
    right = 1
    left_df = total_df.iloc[left]
    rows.append(
            (
                int(left_df["transaction_id"]),
                int(left_df["user_id"]),
                float(left_df["amount"]),
                int(left_df["time"]),
                str(left_df["time_readable"]),
                str(left_df["merchant"]),
                str(left_df["location"]),
                int(left_df["fraud_score"])
            )
        )
    #Utilising sliding window approach
    while right < len(total_df) and left <= right:
        left_df = total_df.iloc[left]
        right_df = total_df.iloc[right]
        rows.append(
            (
                int(right_df["transaction_id"]),
                int(right_df["user_id"]),
                float(right_df["amount"]),
                int(right_df["time"]),
                str(right_df["time_readable"]),
                str(right_df["merchant"]),
                str(right_df["location"]),
                int(right_df["fraud_score"])
            )
        )
        merchant1 = left_df["merchant"]
        merchant2 = right_df["merchant"]
        if merchant1 not in merchants:
            merchants.append(merchant1)
        if merchant2 not in merchants:
            merchants.append(merchant2)
        size = (right - left) + 1#Added one as python starts indexing from 0
        time = right_df["time"] - left_df["time"]

        #Check if 10 or more transactions were made in less than 5 minutes
        #Also check if more than 3 merchants were paid in that timeframe
        if(time <= 300):
            if(size > 10):
                if(len(merchants) > 3):
                    
                    while len(rows) >= 1:
                        current_df = rows.pop()
                        currentMerchant = current_df["merchant"]
                        
                        current_id = int(current_df[0])
                        flagged_ids.add(current_id)
                    #Only one SQL call = better performance
                    cursor.executemany(
                        "UPDATE transactions SET fraud_score = fraud_score + 30 WHERE transaction_id = ?",
                        [(id, ) for id in flagged_ids]
                    )
                    conn.commit()
                    #Remove any merchant that is no longer in the window
                    merchants = []

                    
        else:
            while(time > 300):
                left += 1
                left_df = total_df.iloc[left]
                time = right_df["time"] - left_df["time"]
            foundMerchants = []
            #Remove any merchants that aren't in rows anymore
            for row in rows:
                #Extract current merchant from row tuple
                currentMerchant = row[5]
                if currentMerchant not in foundMerchants:
                    foundMerchants.append(currentMerchant)
            merchants = foundMerchants
        right += 1
def nightTime(id, total_df, conn):
    cursor = conn.cursor()
    #Flag transactions made between 1AM and 4AM as suspicous
    total_df["hour"] = total_df["time_readable"].str.split(":").str[0].astype(int)
    total_df.loc[
        total_df["hour"] >= 1 and total_df["hour"] <= 4,
        "fraud_score"
    ] += 15
#Main function used to detect frauds
def fraudDetector(id, conn, fraud_conn):
    fraud_cursor = fraud_conn.cursor()
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
                fraud_score INTEGER
                )
        """)
    total_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ?",
        con=conn,
        params=[id]
    )
    checkAmount(id, total_df, conn)
    checkLocation(id, total_df, conn)
    transactionNum(id, total_df, conn)
    nightTime(id, total_df, conn)
    total_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ?",
        con=conn,
        params=[id]
    )
    
    #Mark any transaction with a fraud_score >= 70 as suspicous
    
    rows = []
    for i in range(len(total_df)):
        current_df = total_df.iloc[i]
        if(current_df["fraud_score"] >= 70):
            rows.append(
                (
                    int(current_df["transaction_id"]),
                    int(current_df["user_id"]),
                    float(current_df["amount"]),
                    int(current_df["time"]),
                    str(current_df["time_readable"]),
                    str(current_df["merchant"]),
                    str(current_df["location"]),
                    int(current_df["fraud_score"])
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
                    fraud_score
                )
                VALUES (?,?,?,?,?,?,?,?)
                ON CONFLICT(transaction_id) DO UPDATE SET
                    user_id = excluded.user_id,
                    amount = excluded.amount,
                    time = excluded.time,
                    time_readable = excluded.time_readable,
                    merchant = excluded.merchant,
                    location = excluded.location,
                    fraud_score = excluded.fraud_score
                """,
                rows
            )
    fraud_conn.commit()



""" fraudDetector(1)
fraudDetector(2)
fraudDetector(3)
fraudDetector(4)
fraudDetector(5)
df = pd.read_sql_query("SELECT * FROM frauds", con=fraud_conn)
print(df) """
