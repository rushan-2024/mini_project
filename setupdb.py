import sqlite3

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT
)
""")

cursor.execute("INSERT OR IGNORE INTO users VALUES (1,'admin','admin123')")
cursor.execute("INSERT OR IGNORE INTO users VALUES (2,'anuja','pass456')")

conn.commit()
conn.close()

print("Database created")