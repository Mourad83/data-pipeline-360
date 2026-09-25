import sqlite3
from datetime import datetime

from config import (
    DATABASE_PATH,
    RAW_DIR,
    PROCESSED_DIR,
    ARCHIVE_DIR,
    REJECTED_DIR
)

from extract import get_sales_files, read_sales_file
from validate import validate_sales_file
from transform import transform_sales_data
from load import load_sales_data

from file_manager import (
    copy_to_raw,
    save_to_processed,
    move_to_archive,
    move_to_rejected
)

from logger import setup_logger


logger = setup_logger()


print("====================================")
print("DATA PIPELINE 360")
print("====================================")

logger.info("Pipeline started")


sales_files = get_sales_files()

print("Fichiers détectés :", len(sales_files))
print()

logger.info(
    "Files detected: %s",
    len(sales_files)
)


conn = sqlite3.connect(DATABASE_PATH)

conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()


files_success = 0
files_failed = 0
files_skipped = 0

total_rows_read = 0
total_rows_inserted = 0
total_rows_rejected = 0


for file_path in sales_files:

    print("------------------------------------")
    print("Fichier :", file_path.name)

    logger.info(
        "Processing file: %s",
        file_path.name
    )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM File_History
        WHERE FileName = ?
          AND Status = 'SUCCESS'
        """,
        (file_path.name,)
    )

    already_processed = cursor.fetchone()[0]


    # Fichier déjà traité avec succès
    if already_processed > 0:

        print("Statut : SKIPPED")
        print("Fichier déjà traité avec succès.")

        logger.info(
            "File skipped because already processed successfully: %s",
            file_path.name
        )

        try:

            copy_to_raw(
                file_path,
                RAW_DIR
            )

            logger.info(
                "RAW copy created for skipped file: %s",
                file_path.name
            )

            move_to_archive(
                file_path,
                ARCHIVE_DIR
            )

            print("Fichier déplacé vers archive.")

            logger.info(
                "Skipped file moved to archive: %s",
                file_path.name
            )

        except Exception as error:

            print(
                "Erreur lors du déplacement :",
                error
            )

            logger.error(
                "File movement error for %s: %s",
                file_path.name,
                error
            )

        files_skipped += 1

        continue


    try:

        # RAW
        copy_to_raw(
            file_path,
            RAW_DIR
        )

        print("Copie RAW créée.")

        logger.info(
            "RAW copy created: %s",
            file_path.name
        )


        # EXTRACT
        df_sales = read_sales_file(
            file_path
        )

        rows_read = len(df_sales)

        total_rows_read += rows_read

        print(
            "Lignes extraites :",
            rows_read
        )

        logger.info(
            "%s rows extracted from %s",
            rows_read,
            file_path.name
        )


        # VALIDATE
        validation_errors = validate_sales_file(
            df_sales,
            file_path.name,
            conn
        )


        if len(validation_errors) > 0:

            print("Statut : INVALID")

            logger.warning(
                "Validation failed for file: %s",
                file_path.name
            )

            for error in validation_errors:

                print(error)

                logger.error(
                    "%s - %s",
                    file_path.name,
                    error
                )

            error_message = " | ".join(
                validation_errors
            )


            # REJECTED
            move_to_rejected(
                file_path,
                REJECTED_DIR
            )

            print(
                "Fichier déplacé vers rejected."
            )

            logger.info(
                "File moved to rejected: %s",
                file_path.name
            )


            cursor.execute(
                """
                INSERT INTO File_History (
                    FileName,
                    LoadDate,
                    Status,
                    RowsRead,
                    RowsInserted,
                    RowsRejected,
                    ErrorMessage
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(FileName)
                DO UPDATE SET
                    LoadDate = excluded.LoadDate,
                    Status = excluded.Status,
                    RowsRead = excluded.RowsRead,
                    RowsInserted = excluded.RowsInserted,
                    RowsRejected = excluded.RowsRejected,
                    ErrorMessage = excluded.ErrorMessage
                """,
                (
                    file_path.name,
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "FAILED",
                    rows_read,
                    0,
                    rows_read,
                    error_message
                )
            )

            conn.commit()

            logger.info(
                "FAILED status written to File_History: %s",
                file_path.name
            )

            files_failed += 1
            total_rows_rejected += rows_read

            continue


        print(
            "Statut validation : VALID"
        )

        logger.info(
            "Validation successful: %s",
            file_path.name
        )


        # TRANSFORM
        df_transformed = transform_sales_data(
            df_sales
        )

        print(
            "Lignes transformées :",
            len(df_transformed)
        )

        logger.info(
            "%s rows transformed for %s",
            len(df_transformed),
            file_path.name
        )


        # PROCESSED
        save_to_processed(
            df_transformed,
            file_path.name,
            PROCESSED_DIR
        )

        print(
            "Fichier processed créé."
        )

        logger.info(
            "Processed file created: %s",
            file_path.name
        )


        # LOAD
        inserted_rows, ignored_rows = load_sales_data(
            df_transformed,
            conn
        )

        print(
            "Lignes insérées :",
            inserted_rows
        )

        print(
            "Lignes ignorées :",
            ignored_rows
        )

        logger.info(
            "%s rows inserted for %s",
            inserted_rows,
            file_path.name
        )

        logger.info(
            "%s rows ignored for %s",
            ignored_rows,
            file_path.name
        )


        # ARCHIVE
        move_to_archive(
            file_path,
            ARCHIVE_DIR
        )

        print(
            "Fichier déplacé vers archive."
        )

        logger.info(
            "File moved to archive: %s",
            file_path.name
        )


        # FILE HISTORY
        cursor.execute(
            """
            INSERT INTO File_History (
                FileName,
                LoadDate,
                Status,
                RowsRead,
                RowsInserted,
                RowsRejected,
                ErrorMessage
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(FileName)
            DO UPDATE SET
                LoadDate = excluded.LoadDate,
                Status = excluded.Status,
                RowsRead = excluded.RowsRead,
                RowsInserted = excluded.RowsInserted,
                RowsRejected = excluded.RowsRejected,
                ErrorMessage = excluded.ErrorMessage
            """,
            (
                file_path.name,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "SUCCESS",
                rows_read,
                inserted_rows,
                0,
                None
            )
        )

        conn.commit()

        logger.info(
            "SUCCESS status written to File_History: %s",
            file_path.name
        )

        files_success += 1
        total_rows_inserted += inserted_rows


    except Exception as error:

        print("Statut : ERROR")
        print("Erreur :", error)

        logger.exception(
            "Pipeline error while processing file: %s",
            file_path.name
        )

        cursor.execute(
            """
            INSERT INTO File_History (
                FileName,
                LoadDate,
                Status,
                RowsRead,
                RowsInserted,
                RowsRejected,
                ErrorMessage
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(FileName)
            DO UPDATE SET
                LoadDate = excluded.LoadDate,
                Status = excluded.Status,
                RowsRead = excluded.RowsRead,
                RowsInserted = excluded.RowsInserted,
                RowsRejected = excluded.RowsRejected,
                ErrorMessage = excluded.ErrorMessage
            """,
            (
                file_path.name,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "ERROR",
                0,
                0,
                0,
                str(error)
            )
        )

        conn.commit()

        files_failed += 1


cursor.execute(
    "SELECT COUNT(*) FROM Fact_Sales;"
)

fact_sales_count = cursor.fetchone()[0]


cursor.execute(
    "SELECT COUNT(*) FROM File_History;"
)

file_history_count = cursor.fetchone()[0]


conn.close()


print()
print("====================================")
print("RÉSUMÉ DU PIPELINE")
print("====================================")

print(
    "Fichiers détectés :",
    len(sales_files)
)

print(
    "Fichiers SUCCESS :",
    files_success
)

print(
    "Fichiers FAILED / ERROR :",
    files_failed
)

print(
    "Fichiers SKIPPED :",
    files_skipped
)

print(
    "Lignes lues :",
    total_rows_read
)

print(
    "Lignes insérées :",
    total_rows_inserted
)

print(
    "Lignes rejetées :",
    total_rows_rejected
)

print(
    "Lignes dans Fact_Sales :",
    fact_sales_count
)

print(
    "Fichiers dans File_History :",
    file_history_count
)

print("====================================")
print("Pipeline terminé")
print("====================================")


logger.info(
    "Pipeline summary - Files detected: %s | SUCCESS: %s | FAILED/ERROR: %s | SKIPPED: %s | Rows read: %s | Rows inserted: %s | Rows rejected: %s | Fact_Sales: %s | File_History: %s",
    len(sales_files),
    files_success,
    files_failed,
    files_skipped,
    total_rows_read,
    total_rows_inserted,
    total_rows_rejected,
    fact_sales_count,
    file_history_count
)

logger.info("Pipeline finished")
