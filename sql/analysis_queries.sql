-- ============================================================
-- DATA PIPELINE 360
-- SQL ANALYTICAL QUERIES
-- SQLite
-- ============================================================


-- ============================================================
-- 1. GLOBAL SALES KPIs
-- ============================================================

SELECT
    COUNT(DISTINCT OrderID) AS TotalOrders,
    SUM(Quantity) AS TotalQuantity,
    ROUND(SUM(SalesAmount), 2) AS TotalSales,
    ROUND(
        SUM(SalesAmount) / COUNT(DISTINCT OrderID),
        2
    ) AS AverageOrderValue
FROM Fact_Sales;


-- ============================================================
-- 2. MONTHLY SALES PERFORMANCE
-- ============================================================

SELECT
    d.Year,
    d.MonthNumber,
    d.MonthName,
    COUNT(DISTINCT f.OrderID) AS TotalOrders,
    SUM(f.Quantity) AS TotalQuantity,
    ROUND(SUM(f.SalesAmount), 2) AS TotalSales
FROM Fact_Sales f

INNER JOIN Dim_Date d
    ON f.DateKey = d.DateKey

GROUP BY
    d.Year,
    d.MonthNumber,
    d.MonthName

ORDER BY
    d.Year,
    d.MonthNumber;


-- ============================================================
-- 3. SALES BY STORE
-- ============================================================

SELECT
    s.StoreID,
    s.StoreName,
    s.Channel,
    s.City,
    COUNT(DISTINCT f.OrderID) AS TotalOrders,
    SUM(f.Quantity) AS TotalQuantity,
    ROUND(SUM(f.SalesAmount), 2) AS TotalSales
FROM Fact_Sales f

INNER JOIN Dim_Store s
    ON f.StoreID = s.StoreID

GROUP BY
    s.StoreID,
    s.StoreName,
    s.Channel,
    s.City

ORDER BY
    TotalSales DESC;


-- ============================================================
-- 4. TOP CUSTOMERS BY SALES
-- ============================================================

SELECT
    c.CustomerID,
    c.CustomerName,
    c.CustomerSegment,
    COUNT(DISTINCT f.OrderID) AS TotalOrders,
    ROUND(SUM(f.SalesAmount), 2) AS TotalSales
FROM Fact_Sales f

INNER JOIN Dim_Customer c
    ON f.CustomerID = c.CustomerID

GROUP BY
    c.CustomerID,
    c.CustomerName,
    c.CustomerSegment

ORDER BY
    TotalSales DESC

LIMIT 10;


-- ============================================================
-- 5. PRODUCT PERFORMANCE
-- ============================================================

SELECT
    p.ProductID,
    p.ProductName,
    p.Category,
    p.Subcategory,
    SUM(f.Quantity) AS TotalQuantity,
    ROUND(SUM(f.SalesAmount), 2) AS TotalSales
FROM Fact_Sales f

INNER JOIN Dim_Product p
    ON f.ProductID = p.ProductID

GROUP BY
    p.ProductID,
    p.ProductName,
    p.Category,
    p.Subcategory

ORDER BY
    TotalSales DESC;


-- ============================================================
-- 6. CATEGORY PERFORMANCE
-- ============================================================

SELECT
    p.Category,
    COUNT(DISTINCT f.OrderID) AS TotalOrders,
    SUM(f.Quantity) AS TotalQuantity,
    ROUND(SUM(f.SalesAmount), 2) AS TotalSales
FROM Fact_Sales f

INNER JOIN Dim_Product p
    ON f.ProductID = p.ProductID

GROUP BY
    p.Category

ORDER BY
    TotalSales DESC;


-- ============================================================
-- 7. CUSTOMER RANKING
-- CTE + WINDOW FUNCTIONS
-- ============================================================

WITH CustomerSales AS (

    SELECT
        c.CustomerID,
        c.CustomerName,
        ROUND(SUM(f.SalesAmount), 2) AS TotalSales

    FROM Fact_Sales f

    INNER JOIN Dim_Customer c
        ON f.CustomerID = c.CustomerID

    GROUP BY
        c.CustomerID,
        c.CustomerName
)

SELECT
    CustomerID,
    CustomerName,
    TotalSales,

    ROW_NUMBER() OVER (
        ORDER BY TotalSales DESC
    ) AS RowNumber,

    RANK() OVER (
        ORDER BY TotalSales DESC
    ) AS SalesRank,

    DENSE_RANK() OVER (
        ORDER BY TotalSales DESC
    ) AS DenseSalesRank

FROM CustomerSales

ORDER BY
    TotalSales DESC;


-- ============================================================
-- 8. PRODUCT RANKING BY CATEGORY
-- PARTITION BY + DENSE_RANK
-- ============================================================

WITH ProductSales AS (

    SELECT
        p.ProductID,
        p.ProductName,
        p.Category,
        ROUND(SUM(f.SalesAmount), 2) AS TotalSales

    FROM Fact_Sales f

    INNER JOIN Dim_Product p
        ON f.ProductID = p.ProductID

    GROUP BY
        p.ProductID,
        p.ProductName,
        p.Category
)

SELECT
    ProductID,
    ProductName,
    Category,
    TotalSales,

    DENSE_RANK() OVER (
        PARTITION BY Category
        ORDER BY TotalSales DESC
    ) AS CategoryRank

FROM ProductSales

ORDER BY
    Category,
    CategoryRank;


-- ============================================================
-- 9. MONTH-OVER-MONTH SALES ANALYSIS
-- CTE + LAG WINDOW FUNCTION
-- ============================================================

WITH MonthlySales AS (

    SELECT
        d.Year,
        d.MonthNumber,
        d.MonthName,
        ROUND(SUM(f.SalesAmount), 2) AS TotalSales

    FROM Fact_Sales f

    INNER JOIN Dim_Date d
        ON f.DateKey = d.DateKey

    GROUP BY
        d.Year,
        d.MonthNumber,
        d.MonthName
),

SalesEvolution AS (

    SELECT
        Year,
        MonthNumber,
        MonthName,
        TotalSales,

        LAG(TotalSales) OVER (
            ORDER BY Year, MonthNumber
        ) AS PreviousMonthSales

    FROM MonthlySales
)

SELECT
    Year,
    MonthNumber,
    MonthName,
    TotalSales,
    PreviousMonthSales,

    ROUND(
        TotalSales - PreviousMonthSales,
        2
    ) AS SalesVariance,

    ROUND(
        (
            TotalSales - PreviousMonthSales
        ) * 100.0 / NULLIF(PreviousMonthSales, 0),
        2
    ) AS GrowthPercent

FROM SalesEvolution

ORDER BY
    Year,
    MonthNumber;


-- ============================================================
-- 10. SALES VS TARGET
-- ============================================================

WITH MonthlyStoreSales AS (

    SELECT
        d.Year || '-' || printf('%02d', d.MonthNumber) AS TargetMonth,
        f.StoreID,
        ROUND(SUM(f.SalesAmount), 2) AS ActualSales

    FROM Fact_Sales f

    INNER JOIN Dim_Date d
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

    COALESCE(a.ActualSales, 0) AS ActualSales,

    t.SalesTarget,

    ROUND(
        COALESCE(a.ActualSales, 0) - t.SalesTarget,
        2
    ) AS Variance,

    ROUND(
        COALESCE(a.ActualSales, 0)
        * 100.0
        / NULLIF(t.SalesTarget, 0),
        2
    ) AS AchievementPercent

FROM Fact_Targets t

LEFT JOIN MonthlyStoreSales a
    ON t.TargetMonth = a.TargetMonth
    AND t.StoreID = a.StoreID

LEFT JOIN Dim_Store s
    ON t.StoreID = s.StoreID

ORDER BY
    t.TargetMonth,
    t.StoreID;


-- ============================================================
-- 11. PIPELINE FILE PROCESSING MONITORING
-- ============================================================

SELECT
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

    ErrorMessage

FROM File_History

ORDER BY
    LoadDate DESC;


-- ============================================================
-- 12. PIPELINE LOAD SUMMARY
-- ============================================================

SELECT
    Status,
    COUNT(*) AS NumberOfFiles,
    SUM(RowsRead) AS TotalRowsRead,
    SUM(RowsInserted) AS TotalRowsInserted,
    SUM(RowsRejected) AS TotalRowsRejected
FROM File_History

GROUP BY
    Status

ORDER BY
    NumberOfFiles DESC;
