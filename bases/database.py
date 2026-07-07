import sqlite3
from os import getenv
from dotenv import load_dotenv

load_dotenv()

DB_NAME = getenv("DB_NAME")

def init_db():
    #Создает таблицу при запуске бота
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                email TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alarms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                coin TEXT,
                target_price REAL,
                condition TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        conn.commit()

def save_user(user_id, name, age, email):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO users (user_id, name, age, email) VALUES (?, ?, ?, ?)",
            (user_id, name, age, email)
        )
        conn.commit()

def add_alarm(user_id, coin, price, condition):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alarms (user_id, coin, target_price, condition) VALUES (?, ?, ?, ?)",
            (user_id, coin.upper(), price, condition)
        )
        conn.commit()

def get_active_alarms():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, coin, target_price, condition FROM alarms WHERE is_active = 1")
        return cursor.fetchall()

def deactivate_alarm(alarm_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE alarms SET is_active = 0 WHERE id = ?", (alarm_id,))
        conn.commit()