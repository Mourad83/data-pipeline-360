import sqlite3

from config import DATABASE_PATH


conn = sqlite3.connect(DATABASE_PATH)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS File_History (
    FileHistoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    FileName TEXT NOT NULL UNIQUE,
    LoadDate TEXT NOT NULL,
    Status TEXT NOT NULL,
    RowsRead INTEGER DEFAULT 0,
    RowsInserted INTEGER DEFAULT 0,
    RowsRejected INTEGER DEFAULT 0,
    ErrorMessage TEXT
)
""")

conn.commit()

conn.close()

print("Table File_History créée")
