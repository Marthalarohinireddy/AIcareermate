import sqlite3
import hashlib

def create_usertable():
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    hashed_pswd = hashlib.sha256(password.encode()).hexdigest()
    c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, hashed_pswd))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    hashed_pswd = hashlib.sha256(password.encode()).hexdigest()
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, hashed_pswd))
    return c.fetchall()