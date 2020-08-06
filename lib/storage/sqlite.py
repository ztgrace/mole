import json
from .storagedriver import StorageDriver
import sqlite3


class SqliteDriver(StorageDriver):
    def __init__(self, **kwargs):
        super(SqliteDriver, self).__init__(**kwargs)
        self.connection = sqlite3.connect('mole.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tokens (id INTEGER PRIMARY KEY AUTOINCREMENT, token varchar(256) NOT NULL, context json NOT NULL)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, type varchar(256) NOT NULL, token INTEGER, context json NOT NULL)")

    def __del__(self):
        self.connection.close()

    def add_token(self, **kwargs):
        print(json.dumps(kwargs['context']))
        self.cursor.execute("INSERT INTO tokens (token, context) VALUES (?, ?)",
                            (kwargs['token'], json.dumps(kwargs['context'])))
        self.connection.commit()

    def add_event(self, **kwargs):
        self.cursor.execute("INSERT INTO events (type, token, context) VALUES (?, ?, ?)",
                            (kwargs['type'], kwargs['token'], json.dumps(kwargs['context'])))
        self.connection.commit()

    def delete(self, **kwargs):
        pass

    def get_token(self, **kwargs):
        self.cursor.execute("SELECT * FROM tokens WHERE token = ?", kwargs['token'])
        rows = self.cursor.fetchall()
        return rows

    def update(self, **kwargs):
        pass