import sqlite3
import pandas as pd
from datetime import datetime

def init_db():
    conn = sqlite3.connect('crypto_saas.db')
    c = conn.cursor()
    # Create Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT)''')
    # Create History Table with the added 'note' column
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  coin TEXT, 
                  risk_level TEXT, 
                  volatility REAL, 
                  timestamp DATETIME,
                  note TEXT)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    try:
        conn = sqlite3.connect('crypto_saas.db')
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('crypto_saas.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def save_history(username, coin, risk, vol, note=""):
    conn = sqlite3.connect('crypto_saas.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (username, coin, risk_level, volatility, timestamp, note) VALUES (?, ?, ?, ?, ?, ?)",
              (username, coin, risk, vol, datetime.now(), note))
    conn.commit()
    conn.close()

def get_admin_data():
    conn = sqlite3.connect('crypto_saas.db')
    df = pd.read_sql_query("SELECT * FROM history", conn)
    conn.close()
    return df

def delete_history_entry(entry_id):
    conn = sqlite3.connect('crypto_saas.db')
    c = conn.cursor()
    c.execute("DELETE FROM history WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()

def get_system_stats():
    conn = sqlite3.connect('crypto_saas.db')
    users = pd.read_sql_query("SELECT COUNT(*) as count FROM users", conn).iloc[0]['count']
    analyses = pd.read_sql_query("SELECT COUNT(*) as count FROM history", conn).iloc[0]['count']
    conn.close()
    import os
    db_size = os.path.getsize('crypto_saas.db') / 1024
    return {"users": users, "analyses": analyses, "db_size": f"{db_size:.2f} KB"}

def purge_all_history():
    conn = sqlite3.connect('crypto_saas.db')
    c = conn.cursor()
    c.execute("DELETE FROM history")
    conn.commit()
    conn.close()