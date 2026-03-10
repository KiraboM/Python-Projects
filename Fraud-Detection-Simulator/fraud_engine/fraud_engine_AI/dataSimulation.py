import numpy as np
import pandas as pd
#import sklearn as sk
import random
import sqlite3
import matplotlib.pyplot as plt
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fraud_engine.detector import fraudDetector
from fraud_engine.detector import checkAmount
from fraud_engine.detector import checkLocation
from fraud_engine.detector import nightTime
from fraud_engine.detector import transactionNum

company_list = ["Amazon", "Tesco", "Sainsbury's","Netflix", "Uniliever"]
location_list = ["Enlgand", "Scotland", "Wales", "Northen Island"]
name_list = ["Jeff", "Harris", "Jane", "Henry", "Silvia"]

#Generating temporary database to store transactions
db_path = Path(__file__).with_name("transaction.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

db_fraud_path = Path(__file__).with_name("my_frauds.db")
fraud_conn = sqlite3.connect(db_fraud_path)
fraud_cursor = fraud_conn.cursor()

cursor.execute(""" 
CREATE TABLE IF NOT EXISTS transactions(
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

conn.commit()

# Reset generated transactions so reruns always start from a clean dataset.
cursor.execute("DELETE FROM transactions")
conn.commit()

rows = []

for i in range(100000):
    rows.append(
        (random.randint(1, 5),
        max(1 ,random.normalvariate(40, 30)), 
        random.randint(1000000, 1000000000), 
        str(random.randint(0, 23)) + ":" + str(random.randint(1, 59)), 
        random.choice(company_list), 
        random.choice(location_list), 
        0)
    )
cursor.executemany(
    """ INSERT INTO transactions (user_id, amount, time, time_readable, merchant, location, fraud_score)
    VALUES (?, ?, ?, ?, ?, ?, ?) """,
    rows
)

conn.commit()


total_df = pd.read_sql_query(
    "SELECT * FROM transactions",
    con=conn
)

#Generating fraud scores using fraud detector

for i in range(1, 6):
    fraudDetector(i, total_df, conn, fraud_conn)

total_df = pd.read_sql_query(
    "SELECT * FROM transactions",
    con=conn
)


total_df = total_df.sort_values(["user_id", "time"])

#Generating fraud criteria for logistic regression model
#Checking if user makes a transaction in nightime

total_df["hour"] = total_df["time_readable"].str.split(":").str[0].astype(int)
total_df["night_time"] = (total_df["hour"] >= 1) & (total_df["hour"] <= 4)

#Checking the average amount the user spends

total_df["average_amount"] = total_df.groupby("user_id")["amount"].transform("mean")

#Creating feature for amount given transaction deviates from user's mean

total_df["amount_deviation"] = abs((total_df["amount"]) - (total_df["average_amount"]))

#Creating feature for number of transactions a user makes
#fraud
total_df["transaction_amount"] = total_df.groupby("user_id")["transaction_id"].cumcount()

#Creating feature for time since last transaction for given user_id

total_df["prev_time"] = total_df.groupby("user_id")["time"].shift(1)
total_df["time_since_last_transaction"] = total_df["time"] - total_df["prev_time"]

#Creating feature to check if the location has changed

total_df["prev_location"] = total_df.groupby("user_id")["location"].shift(1)
total_df["location_change"] = (total_df["location"] != total_df["prev_location"]).astype(int)

#Creating feature to check how often a user send a transaction to a certain merchant
total_df["merchant_num"] = (total_df.groupby(["user_id", "merchant"])["transaction_id"].cumcount())

#Using Matplotlib to plot a graph of frauds and normal transactions

total_df["fraud_label"] = (total_df["fraud_score"] >= 70).astype(int)

fraud_count = total_df.groupby("fraud_label")["transaction_id"].count()

fraud_count.plot(kind="bar")

plt.xlabel("Fraud Label")
plt.ylabel("Number of Transactions")

print(total_df.head())