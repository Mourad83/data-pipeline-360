import pandas as pd


REQUIRED_COLUMNS = [
    "OrderID",
    "OrderLineID",
    "OrderDate",
    "CustomerID",
    "ProductID",
    "StoreID",
    "Quantity",
    "UnitPrice",
    "Discount",
    "SalesAmount"
]


def validate_sales_file(df, file_name, conn):

    errors = []

    print("Validation du fichier :", file_name)

    # 1. Vérification des colonnes obligatoires
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"Colonnes manquantes : {missing_columns}"
        )

        return errors

    # 2. Vérification des valeurs nulles
    null_counts = df[REQUIRED_COLUMNS].isna().sum()

    columns_with_nulls = null_counts[null_counts > 0]

    if len(columns_with_nulls) > 0:
        errors.append(
            f"Valeurs nulles détectées : {columns_with_nulls.to_dict()}"
        )

    # 3. Vérification des doublons
    duplicate_count = df.duplicated(
        subset=["OrderID", "OrderLineID"]
    ).sum()

    if duplicate_count > 0:
        errors.append(
            f"Doublons détectés : {duplicate_count}"
        )

    # 4. Vérification des dates
    converted_dates = pd.to_datetime(
        df["OrderDate"],
        errors="coerce"
    )

    invalid_dates = converted_dates.isna().sum()

    if invalid_dates > 0:
        errors.append(
            f"Dates invalides : {invalid_dates}"
        )

    # 5. Vérification de Quantity
    quantity_numeric = pd.to_numeric(
        df["Quantity"],
        errors="coerce"
    )

    invalid_quantity_type = quantity_numeric.isna().sum()

    if invalid_quantity_type > 0:
        errors.append(
            f"Quantités non numériques : {invalid_quantity_type}"
        )

    negative_quantities = (
        quantity_numeric < 0
    ).sum()

    if negative_quantities > 0:
        errors.append(
            f"Quantités négatives : {negative_quantities}"
        )

    # 6. Vérification de UnitPrice
    unit_price_numeric = pd.to_numeric(
        df["UnitPrice"],
        errors="coerce"
    )

    invalid_unit_prices = unit_price_numeric.isna().sum()

    if invalid_unit_prices > 0:
        errors.append(
            f"Prix unitaires non numériques : {invalid_unit_prices}"
        )

    # 7. Vérification de Discount
    discount_numeric = pd.to_numeric(
        df["Discount"],
        errors="coerce"
    )

    invalid_discounts = discount_numeric.isna().sum()

    if invalid_discounts > 0:
        errors.append(
            f"Remises non numériques : {invalid_discounts}"
        )

    # 8. Vérification de SalesAmount
    sales_amount_numeric = pd.to_numeric(
        df["SalesAmount"],
        errors="coerce"
    )

    invalid_sales_amounts = sales_amount_numeric.isna().sum()

    if invalid_sales_amounts > 0:
        errors.append(
            f"Montants de vente non numériques : {invalid_sales_amounts}"
        )

    # 9. Vérification du calcul métier
    valid_numeric_rows = (
        quantity_numeric.notna()
        & unit_price_numeric.notna()
        & discount_numeric.notna()
        & sales_amount_numeric.notna()
    )

    calculated_sales_amount = (
        quantity_numeric
        * unit_price_numeric
        - discount_numeric
    ).round(2)

    inconsistent_amounts = (
        valid_numeric_rows
        & (
            calculated_sales_amount
            != sales_amount_numeric.round(2)
        )
    ).sum()

    if inconsistent_amounts > 0:
        errors.append(
            f"SalesAmount incohérents : {inconsistent_amounts}"
        )

    # 10. Vérification des CustomerID
    sql_customers = pd.read_sql_query(
        "SELECT CustomerID FROM Dim_Customer",
        conn
    )

    unknown_customers = df.loc[
        df["CustomerID"].notna()
        & ~df["CustomerID"].isin(sql_customers["CustomerID"]),
        "CustomerID"
    ].unique()

    if len(unknown_customers) > 0:
        errors.append(
            f"CustomerID inconnus : {unknown_customers.tolist()}"
        )

    # 11. Vérification des ProductID
    sql_products = pd.read_sql_query(
        "SELECT ProductID FROM Dim_Product",
        conn
    )

    unknown_products = df.loc[
        df["ProductID"].notna()
        & ~df["ProductID"].isin(sql_products["ProductID"]),
        "ProductID"
    ].unique()

    if len(unknown_products) > 0:
        errors.append(
            f"ProductID inconnus : {unknown_products.tolist()}"
        )

    # 12. Vérification des StoreID
    sql_stores = pd.read_sql_query(
        "SELECT StoreID FROM Dim_Store",
        conn
    )

    unknown_stores = df.loc[
        df["StoreID"].notna()
        & ~df["StoreID"].isin(sql_stores["StoreID"]),
        "StoreID"
    ].unique()

    if len(unknown_stores) > 0:
        errors.append(
            f"StoreID inconnus : {unknown_stores.tolist()}"
        )

    return errors
