import pandas as pd


def transform_sales_data(df):

    df = df.copy()

    text_columns = [
        "OrderID",
        "CustomerID",
        "ProductID",
        "StoreID"
    ]

    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()

    df["OrderDate"] = pd.to_datetime(
        df["OrderDate"]
    )

    df["DateKey"] = (
        df["OrderDate"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    df["OrderLineID"] = df["OrderLineID"].astype(int)

    df["Quantity"] = df["Quantity"].astype(int)

    df["UnitPrice"] = df["UnitPrice"].astype(float)

    df["Discount"] = df["Discount"].astype(float)

    df["SalesAmount"] = df["SalesAmount"].astype(float)

    df = df[
        [
            "OrderID",
            "OrderLineID",
            "DateKey",
            "CustomerID",
            "ProductID",
            "StoreID",
            "Quantity",
            "UnitPrice",
            "Discount",
            "SalesAmount"
        ]
    ]

    return df
