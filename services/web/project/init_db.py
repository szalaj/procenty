import sqlite3
import os

basedir = os.path.abspath(os.path.dirname(__file__))

connection = sqlite3.connect(os.path.join(basedir,'database.db'))


with open(os.path.join(basedir,'schema.sql')) as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (nazwa, haslo) VALUES (?, ?)",
            ('kancelaria', 'wps')
            )

cur.execute("INSERT INTO users (nazwa, haslo) VALUES (?, ?)",
            ('gosc1', 'gosc1')
            )

connection.commit()
connection.close()