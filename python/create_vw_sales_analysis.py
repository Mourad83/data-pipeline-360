import sqlite3

from config import DATABASE_PATH


conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Supprimer la vue si elle existe déjà
cursor.execute("""
DROP VIEW IF EXISTS vw_sales_analysis;
""")

# Créer la nouvelle vue analytique
cursor.execute("""
CREATE VIEW vw_sales_analysis AS

SELECT
    fs.SalesKey,
    fs.OrderID,
    fs.OrderLineID,

    -- DATE
    fs.DateKey,
    d.FullDate,
    d.Year,
    d.MonthNumber,
    d.MonthName,
    d.Quarter,
    d.WeekNumber,
    d.DayOfMonth,
    d.DayName,

    -- CUSTOMER
    fs.CustomerID,
    c.CustomerName,
    c.CustomerSegment,
    c.City AS CustomerCity,
    c.Country AS CustomerCountry,
    c.RegistrationDate,

    -- PRODUCT
    fs.ProductID,
    p.ProductName,
    p.Category,
    p.Subcategory,
    p.UnitCost,
    p.ListPrice,
    p.ActiveFlag AS ProductActiveFlag,

    -- STORE
    fs.StoreID,
    s.StoreName,
    s.Channel,
    s.City AS StoreCity,
    s.Region,
    s.Country AS StoreCountry,
    s.ActiveFlag AS StoreActiveFlag,

    -- SALES
    fs.Quantity,
    fs.UnitPrice,
    fs.Discount,
    fs.SalesAmount

FROM Fact_Sales fs

LEFT JOIN Dim_Date d
    ON fs.DateKey = d.DateKey

LEFT JOIN Dim_Customer c
    ON fs.CustomerID = c.CustomerID

LEFT JOIN Dim_Product p
    ON fs.ProductID = p.ProductID

LEFT JOIN Dim_Store s
    ON fs.StoreID = s.StoreID;
""")

conn.commit()

print("vw_sales_analysis created successfully.")

# Vérifier le nombre de lignes
cursor.execute("""
SELECT COUNT(*)
FROM vw_sales_analysis;
""")

row_count = cursor.fetchone()[0]

print("Number of rows:", row_count)

# Vérifier les colonnes
print("\nColumns:")

cursor.execute("""
PRAGMA table_info(vw_sales_analysis);
""")

for column in cursor.fetchall():
    print(column[1], "|", column[2])

# Afficher 5 lignes de contrôle
print("\nSample data:")

cursor.execute("""
SELECT
    FullDate,
    MonthName,
    CustomerName,
    CustomerSegment,
    ProductName,
    Category,
    StoreName,
    Quantity,
    SalesAmount
FROM vw_sales_analysis
LIMIT 5;
""")

for row in cursor.fetchall():
    print(row)

conn.close()

print("\nDONE")
