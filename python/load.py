def load_sales_data(df, conn):

    cursor = conn.cursor()

    rows = [
        (
            row.OrderID,
            int(row.OrderLineID),
            int(row.DateKey),
            row.CustomerID,
            row.ProductID,
            row.StoreID,
            int(row.Quantity),
            float(row.UnitPrice),
            float(row.Discount),
            float(row.SalesAmount)
        )
        for row in df.itertuples(index=False)
    ]

    cursor.execute(
        "SELECT COUNT(*) FROM Fact_Sales;"
    )

    count_before = cursor.fetchone()[0]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO Fact_Sales (
            OrderID,
            OrderLineID,
            DateKey,
            CustomerID,
            ProductID,
            StoreID,
            Quantity,
            UnitPrice,
            Discount,
            SalesAmount
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows
    )

    conn.commit()

    cursor.execute(
        "SELECT COUNT(*) FROM Fact_Sales;"
    )

    count_after = cursor.fetchone()[0]

    inserted_rows = count_after - count_before

    ignored_rows = len(rows) - inserted_rows

    return inserted_rows, ignored_rows
