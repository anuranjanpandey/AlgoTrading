import sqlite3

class database:
    def __init__(self):
        self.conn = sqlite3.connect('data.db')
        self.c = self.conn.cursor()

    # DB  Functions
    def create_usertable(self):
        self.c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


    def add_userdata(self, username, password):
        self.c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
        self.conn.commit()

    def login_user(self, username, password):
        self.c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
        data = self.c.fetchall()
        return data


    def view_all_users(self):
        self.c.execute('SELECT * FROM userstable')
        data = self.c.fetchall()
        return data
