-- ============================================================
-- DATA PIPELINE 360
-- DATABASE SCHEMA
-- SQLite
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- 1. CUSTOMER DIMENSION
-- ============================================================

CREATE TABLE IF NOT EXISTS Dim_Customer (
    CustomerID TEXT PRIMARY KEY,
    CustomerName TEXT NOT NULL,
    CustomerSegment TEXT,
    City TEXT,
    Country TEXT,
    RegistrationDate TEXT
);


-- ============================================================
-- 2. DATE DIMENSION
-- ============================================================

CREATE TABLE IF NOT EXISTS Dim_Date (
    DateKey INTEGER PRIMARY KEY,
    FullDate TEXT NOT NULL UNIQUE,
    Year INTEGER,
    MonthNumber INTEGER,
    MonthName TEXT,
    Quarter TEXT,
    WeekNumber INTEGER,
    DayOfMonth INTEGER,
    DayName TEXT
);


-- ============================================================
-- 3. PRODUCT DIMENSION
-- ============================================================

CREATE TABLE IF NOT EXISTS Dim_Product (
    ProductID TEXT PRIMARY KEY,
    ProductName TEXT NOT NULL,
    Category TEXT,
    Subcategory TEXT,
    UnitCost REAL,
    ListPrice REAL,
    ActiveFlag TEXT
);


-- ============================================================
-- 4. STORE DIMENSION
-- ============================================================

CREATE TABLE IF NOT EXISTS Dim_Store (
    StoreID TEXT PRIMARY KEY,
    StoreName TEXT NOT NULL,
    Channel TEXT,
    City TEXT,
    Region TEXT,
    Country TEXT,
    ActiveFlag TEXT
);


-- ============================================================
-- 5. SALES FACT TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS Fact_Sales (
    SalesKey INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderID TEXT NOT NULL,
    OrderLineID INTEGER NOT NULL,
    DateKey INTEGER NOT NULL,
    CustomerID TEXT NOT NULL,
    ProductID TEXT NOT NULL,
    StoreID TEXT NOT NULL,
    Quantity INTEGER NOT NULL,
    UnitPrice REAL NOT NULL,
    Discount REAL NOT NULL DEFAULT 0,
    SalesAmount REAL NOT NULL,

    UNIQUE (
        OrderID,
        OrderLineID
    ),

    FOREIGN KEY (DateKey)
        REFERENCES Dim_Date(DateKey),

    FOREIGN KEY (CustomerID)
        REFERENCES Dim_Customer(CustomerID),

    FOREIGN KEY (ProductID)
        REFERENCES Dim_Product(ProductID),

    FOREIGN KEY (StoreID)
        REFERENCES Dim_Store(StoreID)
);


-- ============================================================
-- 6. SALES TARGET FACT TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS Fact_Targets (
    TargetKey INTEGER PRIMARY KEY AUTOINCREMENT,
    TargetMonth TEXT NOT NULL,
    StoreID TEXT NOT NULL,
    SalesTarget REAL NOT NULL,

    UNIQUE (
        TargetMonth,
        StoreID
    ),

    FOREIGN KEY (StoreID)
        REFERENCES Dim_Store(StoreID)
);


-- ============================================================
-- 7. FILE PROCESSING HISTORY
-- ============================================================

CREATE TABLE IF NOT EXISTS File_History (
    FileHistoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    FileName TEXT NOT NULL UNIQUE,
    LoadDate TEXT NOT NULL,
    Status TEXT NOT NULL,
    RowsRead INTEGER DEFAULT 0,
    RowsInserted INTEGER DEFAULT 0,
    RowsRejected INTEGER DEFAULT 0,
    ErrorMessage TEXT
);
