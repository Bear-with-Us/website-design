import sqlite3 as sql
conn = sql.connect("VR3.db")
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS UserInfo (
    phone INTEGER PRIMARY KEY,
    password TEXT UNIQUE NOT NULL,
    class INT
);''')

cur.execute('''CREATE TABLE IF NOT EXISTS Register (
    username TEXT NOT NULL,
    game_id INTEGER NOT NULL,
    FOREIGN KEY (username) REFERENCES UserInfo(phone),
    FOREIGN KEY (game_id) REFERENCES GameInfo(game_id)
);''')

cur.execute('''CREATE TABLE IF NOT EXISTS GameInfo (
    game_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kp TEXT NOT NULL,
    type VARCHAR(10) NOT NULL,
    time DATETIME NOT NULL,
    description TEXT NOT NULL,
    QR_code BLOB
);''')

conn.commit()
conn.close()