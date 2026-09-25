import sqlite3

from config import DATABASE_PATH


conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

tables = [
    "Fact_Sales",
    "Dim_Date",
    "Dim_Product",
    "Dim_Customer",
    "Dim_Store"
]

for table in tables:
    print("\n" + "=" * 60)
    print(table)
    print("=" * 60)

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,)
    )

    exists = cursor.fetchone()

    if exists is None:
        print("TABLE NOT FOUND")
    else:
        cursor.execute(f'PRAGMA table_info("{table}")')
        columns = cursor.fetchall()

        for column in columns:
            column_name = column[1]
            column_type = column[2]
            print(f"{column_name} | {column_type}")

conn.close()

print("\nDONE")
