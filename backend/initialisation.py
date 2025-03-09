import sqlite3 as sql
def initialise_db():
    conn = sql.connect("VR3.db")
    cur = conn.cursor()



    cur.execute('''
    CREATE TABLE IF NOT EXISTS UserInfo (
        phone INTEGER PRIMARY KEY,
        password TEXT UNIQUE NOT NULL,
        class INT
    );''')


    cur.execute('''CREATE TABLE IF NOT EXISTS GameInfo (
        game_id INTEGER PRIMARY KEY,
        reference TEXT NOT NULL
    );''')

    cur.execute('''CREATE TABLE IF NOT EXISTS Register (
            username TEXT NOT NULL,
            game_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES UserInfo(phone),
            FOREIGN KEY (game_id) REFERENCES GameInfo(game_id)
        );''')

    conn.commit()
    conn.close()