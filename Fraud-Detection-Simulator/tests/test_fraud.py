from fraud_engine.detector import fraudDetector
from fraud_engine.detector import checkAmount
from fraud_engine.detector import checkLocation
from fraud_engine.detector import nightTime
from fraud_engine.detector import transactionNum

import sqlite3
from pathlib import Path
import random

db_path = Path(__file__).with_name(":memory:")
conn = sqlite3.connect(db_path)

""" fraud_path = Path(__file__).with_name("Fraud-Data.db")
fraud_conn = sqlite3.connect(fraud_path)
fraud_cursor = fraud_conn.cursor() """
import pandas as pd

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
        [(1,6,10,12347859,"6:30","Tesco","England",0),
        (2,6,10,12347859,"6:30","Tesco","England",0),
        (3,6,10,12347859,"6:30","Tesco","England",0),
        (4,6,10,12347859,"6:30","Tesco","England",0),
        (5,6,10,12347859,"6:30","Tesco","England",0),
        (6,6,10,12347859,"6:30","Tesco","England",0),
        (7,6,10,12347859,"6:30","Tesco","England",0),
        (8,6,200000,12347859,"6:30","Tesco","England",0)]
        
    )
    conn.commit()
    total_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ?",
        con=conn,
        params=[6]
    )
    checkAmount(6, total_df, conn)
    total_df.to_sql(
        name="transactions",
        con=conn,
        if_exists="replace",
        index=False
    )
    this_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ? AND fraud_score > 0",
        con=conn,
        params=[6]
    )
    return this_df

def test_checkLocation():
    conn.executemany(
        """ INSERT INTO transactions (transaction_id, user_id, amount, time, time_readable, merchant, location, fraud_score)
        VALUES (?,?,?,?,?,?,?,?) """,
        [(9,5,30,12347860,"6:30","Tesco","England",0),
        (10,5,40,12347890,"6:31","Tesco","Scotland",0)]
        
    )
    conn.commit()
    total_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ?",
        con=conn,
        params=[5]
    )
    checkLocation(5, total_df, conn)
    this_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ? AND fraud_score > 0",
        con=conn,
        params=[5]
    )
    #Check if fraud transaction was added to database
    #assert len(this_df) == 2
    return this_df

def test_transactionNum():
    conn.executemany(
        """ INSERT INTO transactions (transaction_id, user_id, amount, time, time_readable, merchant, location, fraud_score)
        VALUES (?,?,?,?,?,?,?,?) """,
        [(11,8,30,1,"6:30","Tesco","England",0),
         (12,8,40,3,"6:30","Tesco","Scotland",0),
         (13,8,40,4,"6:30","Amazon","Wales",0),
         (14,8,40,6,"6:30","Amazon","Scotland",0),
         (15,8,40,7,"6:30","Tesco","Wales",0),
         (16,8,40,9,"6:30","Tesco","Scotland",0),
         (17,8,40,12,"6:30","Tesco","Scotland",0),
         (18,8,40,14,"6:30","Netflix","Northen Island",0),
         (19,8,40,14,"6:30","Netflix","Scotland",0),
         (20,8,40,14,"6:30","Netflix","Scotland",0),
         (21,8,40,14,"6:30","Tesco","Scotland",0),
         (22,8,40,14,"6:30","Tesco","Scotland",0),
         (23,8,40,14,"6:30","Tesco","Scotland",0)]
        
    )
    conn.commit()
    total_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ?",
        con=conn,
        params=[8]
    )
    transactionNum(8, total_df, conn)
    this_df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id = ? AND fraud_score >= 30",
        con=conn,
        params=[8]
    )
    #Check if the faulty transactions were added to the database
    #assert len(this_df) == 13
    return this_df

checkAmount_df = test_checkAmount()
checkLocation_df = test_checkLocation()
transactionNum_df = test_transactionNum()
assert len(checkAmount_df) == 1
assert len(checkLocation_df) == 2
assert len(transactionNum_df) == 13
conn.close()