import sqlite3 as sql
conn = sql.connect("VR3.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
for table in tables:
            print(table[0])