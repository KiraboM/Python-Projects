from fraud_engine.detector import fraudDetector
from fraud_engine.detector import checkAmount
from fraud_engine.detector import checkLocation
from fraud_engine.detector import nightTime
from fraud_engine.detector import transactionNum

import sqlite3
from pathlib import Path
import random

db_path = Path(__file__).with_name("fraud_simulator.db")
conn = sqlite3.connect(db_path)

fraud_path = Path(__file__).with_name("Fraud-Data.db")
fraud_conn = sqlite3.connect(fraud_path)
fraud_cursor = fraud_conn.cursor()
#hello!
import pandas as pd

conn.execute("DROP TABLE transactions")

conn.execute(""" 
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

def test_checkAmount():
    conn.executemany(
        """ INSERT INTO transactions (transaction_id, user_id, amount, time, time_readable, merchant, location, fraud_score)
        VALUES (?,?,?,?,?,?,?,?) """,
        [(1,6,30,12347859,"6:30","Tesco","England",0),
        (2,6,40,12347859,"6:30","Tesco","England",0),
        (3,6,20000,12347859,"6:30","Tesco","England",0)]
        
    )
    conn.commit()
    total_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ?",
        con=conn,
        params=[6]
    )
    checkAmount(6, total_df, conn)
    this_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ? AND fraud_score > 0",
        con=fraud_conn,
        params=[6]
    )
    #Check if faulty transaction was added to database
    assert len(this_df) == 1
    assert this_df.iloc[0]["transaction_id"] == 3
    assert this_df.iloc[0]["fraud_score"] == 40

def test_checkLocation():
    conn.executemany(
        """ INSERT INTO transactions (transaction_id, user_id, amount, time, time_readable, merchant, location, fraud_score)
        VALUES (?,?,?,?,?,?,?,?) """,
        [(1,5,30,12347860,"6:30","Tesco","England",0),
        (2,5,40,12347859,"6:30","Tesco","Scotland",0)]
        
    )
    conn.commit()
    total_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ?",
        con=conn,
        params=[6]
    )
    checkLocation(5, total_df, conn)
    this_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ? AND fraud_score > 0",
        con=fraud_conn,
        params=[6]
    )
    #Check if fraud transaction was added to database
    assert len(this_df) >= 2
