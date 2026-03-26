-- ══════════════════════════════════════════════════════════
-- Star Schema — Supply Chain Database
-- شغّل هذا في SSMS بعد إنشاء قاعدة البيانات
-- ══════════════════════════════════════════════════════════

CREATE DATABASE SupplyChainDW;
GO
USE SupplyChainDW;
GO

-- ─────────────────────────────────────────
-- 1. جدول التاريخ (Dimension)
-- ─────────────────────────────────────────
CREATE TABLE Dim_Date (
    DateKey         DATE         NOT NULL PRIMARY KEY,
    Year            SMALLINT     NOT NULL,
    Quarter         CHAR(2)      NOT NULL,
    Month_Num       TINYINT      NOT NULL,
    Month_Name      VARCHAR(10)  NOT NULL,
    Week_Number     TINYINT      NOT NULL,
    Day_of_Week     VARCHAR(10)  NOT NULL,
    Is_Weekend      BIT          NOT NULL DEFAULT 0,
    Year_Month      CHAR(7)      NOT NULL,
    Fiscal_Quarter  VARCHAR(10)  NOT NULL
);

-- ─────────────────────────────────────────
-- 2. جدول العميل (Dimension)
-- ─────────────────────────────────────────
CREATE TABLE Dim_Customer (
    Customer_ID          INT          NOT NULL PRIMARY KEY,
    Customer_Segment     VARCHAR(50)  NOT NULL,
    Customer_City        VARCHAR(100) NOT NULL,
    Customer_State       VARCHAR(100) NOT NULL,
    Customer_Country     VARCHAR(100) NOT NULL,
    Market               VARCHAR(50)  NOT NULL,
    Customer_Full_Location VARCHAR(200) NOT NULL
);

-- ─────────────────────────────────────────
-- 3. جدول المنتج (Dimension)
-- ─────────────────────────────────────────
CREATE TABLE Dim_Product (
    Product_Card_ID     INT           NOT NULL PRIMARY KEY,
    Product_Name        VARCHAR(255)  NOT NULL,
    Product_Price       DECIMAL(10,2) NOT NULL,
    Stock_Status        VARCHAR(20)   NOT NULL,
    Category_ID         INT           NOT NULL,
    Category_Name       VARCHAR(100)  NOT NULL,
    Department_ID       INT           NOT NULL,
    Department_Name     VARCHAR(100)  NOT NULL,
    Price_Range         VARCHAR(50)   NOT NULL
);

-- ─────────────────────────────────────────
-- 4. جدول الطلب (Dimension)
-- ─────────────────────────────────────────
CREATE TABLE Dim_Order (
    Order_ID          INT          NOT NULL PRIMARY KEY,
    Order_Status      VARCHAR(50)  NOT NULL,
    Status_Group      VARCHAR(30)  NOT NULL,
    Shipping_Mode     VARCHAR(50)  NOT NULL,
    Delivery_Status   VARCHAR(50)  NOT NULL,
    Delivery_Risk_Flag VARCHAR(20) NOT NULL,
    Order_Region      VARCHAR(100) NOT NULL,
    Order_Country     VARCHAR(100) NOT NULL,
    Order_City        VARCHAR(100) NOT NULL,
    Order_State       VARCHAR(100) NOT NULL,
    Transaction_Type  VARCHAR(50)  NOT NULL
);

-- ─────────────────────────────────────────
-- 5. جدول الحقائق (Fact Table)
-- ─────────────────────────────────────────
CREATE TABLE Fact_Orders (
    Fact_ID                   BIGINT IDENTITY(1,1) PRIMARY KEY,
    Order_ID                  INT           NOT NULL,
    Order_Item_ID             INT           NOT NULL,
    Customer_ID               INT           NOT NULL,
    Product_Card_ID           INT           NOT NULL,
    Order_DateKey             DATE          NOT NULL,
    Shipping_DateKey          DATE          NOT NULL,

    -- المبيعات والأرباح
    Sales                     DECIMAL(12,2) NOT NULL DEFAULT 0,
    Net_Revenue               DECIMAL(12,2) NOT NULL DEFAULT 0,
    Order_Profit              DECIMAL(12,2) NOT NULL DEFAULT 0,
    Benefit_Per_Order         DECIMAL(12,2) NOT NULL DEFAULT 0,
    Sales_Per_Customer        DECIMAL(12,2) NOT NULL DEFAULT 0,

    -- تفاصيل العنصر
    Item_Quantity             INT           NOT NULL DEFAULT 0,
    Item_Discount             DECIMAL(10,2) NOT NULL DEFAULT 0,
    Item_Discount_Rate        DECIMAL(5,4)  NOT NULL DEFAULT 0,
    Item_Product_Price        DECIMAL(10,2) NOT NULL DEFAULT 0,
    Item_Profit_Ratio         DECIMAL(5,4)  NOT NULL DEFAULT 0,
    Item_Total                DECIMAL(12,2) NOT NULL DEFAULT 0,
    Profit_Tier               VARCHAR(20)   NOT NULL,

    -- الشحن
    Shipping_Days_Actual      INT           NOT NULL DEFAULT 0,
    Shipping_Days_Scheduled   INT           NOT NULL DEFAULT 0,
    Shipping_Delay_Days       INT           NOT NULL DEFAULT 0,
    Shipping_Performance      VARCHAR(20)   NOT NULL,
    Late_Delivery_Risk        BIT           NOT NULL DEFAULT 0,

    -- تصنيفات
    Is_Fraud                  VARCHAR(15)   NOT NULL DEFAULT 'Legitimate',

    -- Foreign Keys
    CONSTRAINT FK_Fact_Order     FOREIGN KEY (Order_ID)        REFERENCES Dim_Order(Order_ID),
    CONSTRAINT FK_Fact_Customer  FOREIGN KEY (Customer_ID)     REFERENCES Dim_Customer(Customer_ID),
    CONSTRAINT FK_Fact_Product   FOREIGN KEY (Product_Card_ID) REFERENCES Dim_Product(Product_Card_ID),
    CONSTRAINT FK_Fact_DateO     FOREIGN KEY (Order_DateKey)   REFERENCES Dim_Date(DateKey),
    CONSTRAINT FK_Fact_DateS     FOREIGN KEY (Shipping_DateKey)REFERENCES Dim_Date(DateKey)
);

-- ─────────────────────────────────────────
-- 6. جدول سجلات الموقع (Fact Table)
-- ─────────────────────────────────────────
CREATE TABLE Fact_WebLogs (
    Log_ID          BIGINT IDENTITY(1,1) PRIMARY KEY,
    Product_Name    VARCHAR(255) NOT NULL,
    Category_Name   VARCHAR(100) NOT NULL,
    Log_Date        DATETIME     NOT NULL,
    Year            SMALLINT     NOT NULL,
    Month_Num       TINYINT      NOT NULL,
    Month_Name      VARCHAR(10)  NOT NULL,
    Hour            TINYINT      NOT NULL,
    Hour_Group      VARCHAR(30)  NOT NULL,
    Department      VARCHAR(100) NOT NULL,
    IP_Address      VARCHAR(50)  NOT NULL,
    URL             VARCHAR(500) NOT NULL,
    Is_Add_To_Cart  BIT          NOT NULL DEFAULT 0,
    Action_Type     VARCHAR(30)  NOT NULL
);

-- ─────────────────────────────────────────
-- 7. Indexes للأداء
-- ─────────────────────────────────────────
CREATE INDEX IX_Fact_Orders_Date       ON Fact_Orders (Order_DateKey);
CREATE INDEX IX_Fact_Orders_Customer   ON Fact_Orders (Customer_ID);
CREATE INDEX IX_Fact_Orders_Product    ON Fact_Orders (Product_Card_ID);
CREATE INDEX IX_Fact_Orders_Order      ON Fact_Orders (Order_ID);
CREATE INDEX IX_Fact_WebLogs_Date      ON Fact_WebLogs (Log_Date);
CREATE INDEX IX_Fact_WebLogs_Product   ON Fact_WebLogs (Product_Name);

-- ─────────────────────────────────────────
-- 8. Views مفيدة للتقارير
-- ─────────────────────────────────────────

-- ملخص المبيعات الشهرية
CREATE VIEW vw_Monthly_Sales AS
SELECT
    d.Year,
    d.Quarter,
    d.Month_Num,
    d.Month_Name,
    d.Year_Month,
    COUNT(DISTINCT f.Order_ID)       AS Total_Orders,
    SUM(f.Sales)                     AS Total_Sales,
    SUM(f.Order_Profit)              AS Total_Profit,
    SUM(f.Net_Revenue)               AS Net_Revenue,
    CAST(SUM(f.Order_Profit) * 100.0
         / NULLIF(SUM(f.Sales),0)
         AS DECIMAL(5,2))            AS Profit_Margin_Pct
FROM Fact_Orders f
JOIN Dim_Date d ON f.Order_DateKey = d.DateKey
GROUP BY d.Year, d.Quarter, d.Month_Num, d.Month_Name, d.Year_Month;
GO

-- ملخص أداء الشحن
CREATE VIEW vw_Shipping_Performance AS
SELECT
    o.Shipping_Mode,
    o.Delivery_Status,
    o.Order_Region,
    COUNT(*)                         AS Total_Orders,
    AVG(f.Shipping_Days_Actual)      AS Avg_Actual_Days,
    AVG(f.Shipping_Days_Scheduled)   AS Avg_Scheduled_Days,
    AVG(f.Shipping_Delay_Days)       AS Avg_Delay_Days,
    SUM(f.Late_Delivery_Risk)        AS Late_Count
FROM Fact_Orders f
JOIN Dim_Order o ON f.Order_ID = o.Order_ID
GROUP BY o.Shipping_Mode, o.Delivery_Status, o.Order_Region;
GO

-- أفضل 10 منتجات
CREATE VIEW vw_Top10_Products AS
SELECT TOP 10
    p.Product_Name,
    p.Category_Name,
    p.Department_Name,
    p.Price_Range,
    SUM(f.Item_Quantity)    AS Units_Sold,
    SUM(f.Sales)            AS Total_Sales,
    SUM(f.Order_Profit)     AS Total_Profit,
    AVG(f.Item_Profit_Ratio)AS Avg_Profit_Ratio
FROM Fact_Orders f
JOIN Dim_Product p ON f.Product_Card_ID = p.Product_Card_ID
GROUP BY p.Product_Name, p.Category_Name, p.Department_Name, p.Price_Range
ORDER BY Total_Sales DESC;
GO

-- تحليل الاحتيال
CREATE VIEW vw_Fraud_Analysis AS
SELECT
    o.Order_Region,
    o.Order_Country,
    o.Shipping_Mode,
    d.Year,
    d.Month_Name,
    COUNT(*)              AS Fraud_Orders,
    SUM(f.Sales)          AS Fraud_Revenue_Loss,
    AVG(f.Sales)          AS Avg_Fraud_Order_Value
FROM Fact_Orders f
JOIN Dim_Order o ON f.Order_ID = o.Order_ID
JOIN Dim_Date  d ON f.Order_DateKey = d.DateKey
WHERE f.Is_Fraud = 'Fraud'
GROUP BY o.Order_Region, o.Order_Country, o.Shipping_Mode, d.Year, d.Month_Name;
GO
