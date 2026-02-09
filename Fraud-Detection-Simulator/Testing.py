import sqlite3
from pathlib import Path

import random

db_path = Path(__file__).with_name("fraud_simulator.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

import pandas as pd

df = pd.read_sql_query("SELECT * FROM transactions", con=conn)


