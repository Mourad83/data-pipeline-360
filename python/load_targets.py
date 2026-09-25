import sqlite3
import pandas as pd

from config import TARGETS_DIR, DATABASE_PATH


target_files = sorted(
    TARGETS_DIR.glob("targets_*.csv")
)

print("Fichiers targets détectés :", len(target_files))


conn = sqlite3.connect(DATABASE_PATH)
conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()


total_rows_read = 0
total_rows_inserted = 0
total_rows_ignored = 0


for file_path in target_files:

    print("------------------------------------")
    print("Traitement :", file_path.name)

    df_target = pd.read_csv(file_path)

    rows_read = len(df_target)
    total_rows_read += rows_read

    rows = [
        (
            str(row.TargetMonth).strip(),
            str(row.StoreID).strip(),
            float(row.SalesTarget)
        )
        for row in df_target.itertuples(index=False)
    ]

    cursor.execute(
        "SELECT COUNT(*) FROM Fact_Targets;"
    )

    count_before = cursor.fetchone()[0]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO Fact_Targets (
            TargetMonth,
            StoreID,
            SalesTarget
        )
        VALUES (?, ?, ?)
        """,
        rows
    )

    conn.commit()

    cursor.execute(
        "SELECT COUNT(*) FROM Fact_Targets;"
    )

    count_after = cursor.fetchone()[0]

    inserted_rows = count_after - count_before
    ignored_rows = rows_read - inserted_rows

    total_rows_inserted += inserted_rows
    total_rows_ignored += ignored_rows

    print("Lignes lues :", rows_read)
    print("Lignes insérées :", inserted_rows)
    print("Lignes ignorées :", ignored_rows)


cursor.execute(
    "SELECT COUNT(*) FROM Fact_Targets;"
)

total_targets = cursor.fetchone()[0]


print("====================================")
print("RÉSUMÉ TARGETS")
print("Lignes lues :", total_rows_read)
print("Lignes insérées :", total_rows_inserted)
print("Lignes ignorées :", total_rows_ignored)
print("Fact_Targets :", total_targets)
print("====================================")


conn.close()
