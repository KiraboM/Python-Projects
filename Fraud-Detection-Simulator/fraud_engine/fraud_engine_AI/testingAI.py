from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import sklearn as sk
import random
import sqlite3
from pathlib import Path

db_path = Path(__file__).with_name("transaction.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

total_df = pd.read_sql_query(
    "SELECT * FROM transactions",
    con=conn
)

total_df["fraud_label"] = total_df["fraud_score"] >= 70

features = [
    "night_time",
    "average_amount",
    "amount_deviation",
    "transaction_amount",
    "time_since_last_transaction",
    "location_change",
    "merchant_num"
]

X = total_df[features].fillna(0)

Y = total_df["fraud_label"]

X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42
)

model = LogisticRegression(max_iter=1000)

model.fit(X_train, Y_train)

print("Accuracy: ", model.score(X_test, Y_test))