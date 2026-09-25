-- ============================================================
-- DATA PIPELINE 360
-- ANALYTICAL VIEWS
-- SQLite
-- ============================================================


-- ============================================================
-- 1. SALES ANALYSIS
-- ============================================================

DROP VIEW IF EXISTS vw_sales_analysis;

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


-- ============================================================
-- 2. DAILY SALES
-- ============================================================

DROP VIEW IF EXISTS vw_sales_daily;

CREATE VIEW vw_sales_daily AS

SELECT
    d.DateKey,
    d.FullDate,
    d.Year,
    d.MonthNumber,
    d.MonthName,

    COUNT(DISTINCT f.OrderID) AS TotalOrders,
    SUM(f.Quantity) AS TotalQuantity,
    ROUND(SUM(f.SalesAmount), 2) AS TotalSales,

    ROUND(
        SUM(f.SalesAmount) / COUNT(DISTINCT f.OrderID),
        2
    ) AS AverageOrderValue

FROM Fact_Sales f

LEFT JOIN Dim_Date d
    ON f.DateKey = d.DateKey

GROUP BY
    d.DateKey,
    d.FullDate,
    d.Year,
    d.MonthNumber,
    d.MonthName;


-- ============================================================
-- 3. MONTHLY SALES
-- ============================================================

DROP VIEW IF EXISTS vw_sales_monthly;

CREATE VIEW vw_sales_monthly AS

SELECT
    d.Year,
    d.MonthNumber,
    d.MonthName,

    d.Year || '-' || printf('%02d', d.MonthNumber) AS MonthKey,

    COUNT(DISTINCT f.OrderID) AS TotalOrders,
    SUM(f.Quantity) AS TotalQuantity,
    ROUND(SUM(f.SalesAmount), 2) AS TotalSales,

    ROUND(
        SUM(f.SalesAmount) / COUNT(DISTINCT f.OrderID),
        2
    ) AS AverageOrderValue

FROM Fact_Sales f

LEFT JOIN Dim_Date d
    ON f.DateKey = d.DateKey

GROUP BY
    d.Year,
    d.MonthNumber,
    d.MonthName;


-- ============================================================
-- 4. CUSTOMER PERFORMANCE
-- ============================================================

DROP VIEW IF EXISTS vw_customer_performance;

CREATE VIEW vw_customer_performance AS

WITH CustomerSales AS (

    SELECT
        c.CustomerID,
        c.CustomerName,
        c.CustomerSegment,
        c.City,

        COUNT(DISTINCT f.OrderID) AS TotalOrders,
        SUM(f.Quantity) AS TotalQuantity,
        ROUND(SUM(f.SalesAmount), 2) AS TotalSales,

        ROUND(
            SUM(f.SalesAmount) / COUNT(DISTINCT f.OrderID),
            2
        ) AS AverageOrderValue

    FROM Fact_Sales f

    LEFT JOIN Dim_Customer c
        ON f.CustomerID = c.CustomerID

    GROUP BY
        c.CustomerID,
        c.CustomerName,
        c.CustomerSegment,
        c.City
)

SELECT
    CustomerID,
    CustomerName,
    CustomerSegment,
    City,
    TotalOrders,
    TotalQuantity,
    TotalSales,
    AverageOrderValue,

    DENSE_RANK() OVER (
        ORDER BY TotalSales DESC
    ) AS SalesRank

FROM CustomerSales;


-- ============================================================
-- 5. PRODUCT PERFORMANCE
-- ============================================================

DROP VIEW IF EXISTS vw_product_performance;

CREATE VIEW vw_product_performance AS

WITH ProductSales AS (

    SELECT
        p.ProductID,
        p.ProductName,
        p.Category,
        p.Subcategory,

        COUNT(DISTINCT f.OrderID) AS TotalOrders,
        SUM(f.Quantity) AS TotalQuantity,
        ROUND(SUM(f.SalesAmount), 2) AS TotalSales

    FROM Fact_Sales f

    LEFT JOIN Dim_Product p
        ON f.ProductID = p.ProductID

    GROUP BY
        p.ProductID,
        p.ProductName,
        p.Category,
        p.Subcategory
)

SELECT
    ProductID,
    ProductName,
    Category,
    Subcategory,
    TotalOrders,
    TotalQuantity,
    TotalSales,

    DENSE_RANK() OVER (
        ORDER BY TotalSales DESC
    ) AS SalesRank

FROM ProductSales;


-- ============================================================
-- 6. SALES VS TARGET
-- ============================================================

DROP VIEW IF EXISTS vw_sales_vs_target;

CREATE VIEW vw_sales_vs_target AS

WITH ActualSales AS (

    SELECT
        d.Year || '-' || printf('%02d', d.MonthNumber) AS TargetMonth,
        f.StoreID,

        COUNT(DISTINCT f.OrderID) AS TotalOrders,
        SUM(f.Quantity) AS TotalQuantity,
        ROUND(SUM(f.SalesAmount), 2) AS ActualSales

    FROM Fact_Sales f

    LEFT JOIN Dim_Date d
        ON f.DateKey = d.DateKey

    GROUP BY
        d.Year,
        d.MonthNumber,
        f.StoreID
)

SELECT
    t.TargetMonth,
    t.StoreID,
    s.StoreName,
    s.Channel,
    s.City,

    a.TotalOrders,
    a.TotalQuantity,

    COALESCE(a.ActualSales, 0) AS ActualSales,

    t.SalesTarget,

    ROUND(
        COALESCE(a.ActualSales, 0) - t.SalesTarget,
        2
    ) AS Variance,

    ROUND(
        (
            COALESCE(a.ActualSales, 0) - t.SalesTarget
        ) * 100.0 / t.SalesTarget,
        2
    ) AS VariancePercent,

    ROUND(
        COALESCE(a.ActualSales, 0) * 100.0 / t.SalesTarget,
        2
    ) AS AchievementPercent

FROM Fact_Targets t

LEFT JOIN ActualSales a
    ON t.TargetMonth = a.TargetMonth
    AND t.StoreID = a.StoreID

LEFT JOIN Dim_Store s
    ON t.StoreID = s.StoreID;


-- ============================================================
-- 7. DATA QUALITY MONITORING
-- ============================================================

DROP VIEW IF EXISTS vw_data_quality;

CREATE VIEW vw_data_quality AS

SELECT
    FileHistoryID,
    FileName,
    LoadDate,
    Status,
    RowsRead,
    RowsInserted,
    RowsRejected,

    CASE
        WHEN RowsRead = 0 THEN 0
        ELSE ROUND(
            RowsRejected * 100.0 / RowsRead,
            2
        )
    END AS RejectionRate,

    CASE
        WHEN Status = 'SUCCESS' THEN 'OK'
        ELSE 'TO CHECK'
    END AS QualityStatus,

    ErrorMessage

FROM File_History;
