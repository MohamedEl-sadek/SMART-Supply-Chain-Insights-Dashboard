CREATE DATABASE SupplyChainDW
    COLLATE SQL_Latin1_General_CP1_CI_AS;
GO
USE SupplyChainDW;
GO

CREATE TABLE Dim_Date (
    DateKey         DATE         NOT NULL,
    Year            SMALLINT     NOT NULL,
    Quarter         CHAR(2)      NOT NULL,
    Month_Num       TINYINT      NOT NULL,
    Month_Name      VARCHAR(10)  NOT NULL,
    Week_Number     TINYINT      NOT NULL,
    Day_of_Week     VARCHAR(10)  NOT NULL,
    Is_Weekend      BIT          NOT NULL DEFAULT 0,
    Year_Month      CHAR(7)      NOT NULL,
    Fiscal_Quarter  VARCHAR(12)  NOT NULL,
    CONSTRAINT PK_Dim_Date PRIMARY KEY (DateKey)
);
GO

CREATE TABLE Dim_Customer (
    Customer_ID             INT          NOT NULL,
    Customer_Segment        VARCHAR(50)  NOT NULL,
    Customer_City           VARCHAR(100) NOT NULL,
    Customer_State          VARCHAR(100) NOT NULL,
    Customer_Country        VARCHAR(100) NOT NULL,
    Market                  VARCHAR(50)  NOT NULL,
    Customer_Full_Location  VARCHAR(200) NOT NULL,
    CONSTRAINT PK_Dim_Customer PRIMARY KEY (Customer_ID)
);
GO

CREATE TABLE Dim_Product (
    Product_Card_ID   INT            NOT NULL,
    Product_Name      VARCHAR(255)   NOT NULL,
    Product_Price     DECIMAL(10,2)  NOT NULL,
    Product_Status    TINYINT        NOT NULL,
    Stock_Status      VARCHAR(20)    NOT NULL,
    Category_ID       INT            NOT NULL,
    Category_Name     VARCHAR(100)   NOT NULL,
    Department_ID     INT            NOT NULL,
    Department_Name   VARCHAR(100)   NOT NULL,
    Price_Range       VARCHAR(50)    NOT NULL,
    CONSTRAINT PK_Dim_Product PRIMARY KEY (Product_Card_ID)
);
GO

CREATE TABLE Dim_Order (
    Order_ID            INT          NOT NULL,
    Order_Status        VARCHAR(50)  NOT NULL,
    Status_Group        VARCHAR(30)  NOT NULL,
    Shipping_Mode       VARCHAR(50)  NOT NULL,
    Delivery_Status     VARCHAR(50)  NOT NULL,
    Delivery_Risk_Flag  VARCHAR(20)  NOT NULL,
    Order_Region        VARCHAR(100) NOT NULL,
    Order_Country       VARCHAR(100) NOT NULL,
    Order_City          VARCHAR(100) NOT NULL,
    Order_State         VARCHAR(100) NOT NULL,
    Transaction_Type    VARCHAR(50)  NOT NULL,
    CONSTRAINT PK_Dim_Order PRIMARY KEY (Order_ID)
);
GO

CREATE TABLE Fact_Orders (
    Fact_ID                  BIGINT IDENTITY(1,1) NOT NULL,
    Order_ID                 INT            NOT NULL,
    Order_Item_ID            INT            NOT NULL,
    Customer_ID              INT            NOT NULL,
    Product_Card_ID          INT            NOT NULL,
    Order_DateKey            DATE           NOT NULL,
    Shipping_DateKey         DATE           NOT NULL,
    Sales                    DECIMAL(12,2)  NOT NULL DEFAULT 0,
    Net_Revenue              DECIMAL(12,2)  NOT NULL DEFAULT 0,
    Order_Profit             DECIMAL(12,2)  NOT NULL DEFAULT 0,
    Benefit_Per_Order        DECIMAL(12,2)  NOT NULL DEFAULT 0,
    Sales_Per_Customer       DECIMAL(12,2)  NOT NULL DEFAULT 0,
    Item_Quantity            INT            NOT NULL DEFAULT 0,
    Item_Discount            DECIMAL(10,2)  NOT NULL DEFAULT 0,
    Item_Discount_Rate       DECIMAL(6,4)   NOT NULL DEFAULT 0,
    Item_Product_Price       DECIMAL(10,2)  NOT NULL DEFAULT 0,
    Item_Profit_Ratio        DECIMAL(6,4)   NOT NULL DEFAULT 0,
    Item_Total               DECIMAL(12,2)  NOT NULL DEFAULT 0,
    Shipping_Days_Actual     INT            NOT NULL DEFAULT 0,
    Shipping_Days_Scheduled  INT            NOT NULL DEFAULT 0,
    Shipping_Delay_Days      INT            NOT NULL DEFAULT 0,
    Shipping_Performance     VARCHAR(20)    NOT NULL,
    Late_Delivery_Risk       BIT            NOT NULL DEFAULT 0,
    Is_Fraud                 VARCHAR(15)    NOT NULL DEFAULT 'Legitimate',
    Profit_Category          VARCHAR(20)    NOT NULL,
    Profit_Tier              VARCHAR(20)    NOT NULL,
    Discount_Tier            VARCHAR(30)    NOT NULL,
    Order_Year               SMALLINT       NOT NULL,
    Order_Month              TINYINT        NOT NULL,
    Order_Month_Name         VARCHAR(10)    NOT NULL,
    Order_Quarter            CHAR(2)        NOT NULL,
    Order_Day_of_Week        VARCHAR(10)    NOT NULL,
    Order_Week_Number        TINYINT        NOT NULL,
    CONSTRAINT PK_Fact_Orders    PRIMARY KEY (Fact_ID),
    CONSTRAINT FK_Fact_Order     FOREIGN KEY (Order_ID)         REFERENCES Dim_Order(Order_ID),
    CONSTRAINT FK_Fact_Customer  FOREIGN KEY (Customer_ID)      REFERENCES Dim_Customer(Customer_ID),
    CONSTRAINT FK_Fact_Product   FOREIGN KEY (Product_Card_ID)  REFERENCES Dim_Product(Product_Card_ID),
    CONSTRAINT FK_Fact_DateO     FOREIGN KEY (Order_DateKey)    REFERENCES Dim_Date(DateKey),
    CONSTRAINT FK_Fact_DateS     FOREIGN KEY (Shipping_DateKey) REFERENCES Dim_Date(DateKey)
);
GO

CREATE TABLE Fact_WebLogs (
    Log_ID          BIGINT IDENTITY(1,1) NOT NULL,
    Product_Name    VARCHAR(255) NOT NULL,
    Category_Name   VARCHAR(100) NOT NULL,
    Log_Date        DATETIME     NOT NULL,
    Log_Year        SMALLINT     NOT NULL,
    Log_Month_Num   TINYINT      NOT NULL,
    Log_Day         TINYINT      NOT NULL,
    Log_Hour        TINYINT      NOT NULL,
    Hour_Group      VARCHAR(30)  NOT NULL,
    Department      VARCHAR(100) NOT NULL,
    IP_Address      VARCHAR(50)  NOT NULL,
    URL             VARCHAR(500) NOT NULL,
    Is_Add_To_Cart  BIT          NOT NULL DEFAULT 0,
    Action_Type     VARCHAR(30)  NOT NULL,
    CONSTRAINT PK_Fact_WebLogs PRIMARY KEY (Log_ID)
);
GO

----------------
USE SupplyChainDW;
GO
-- 1.1 Overall KPIs
SELECT
    COUNT(DISTINCT Order_ID)                                        AS Total_Orders,
    COUNT(*)                                                        AS Total_Line_Items,
    SUM(Sales)                                                      AS Total_Sales,
    SUM(Net_Revenue)                                                AS Total_Net_Revenue,
    SUM(Order_Profit)                                               AS Total_Profit,
    SUM(Item_Discount)                                              AS Total_Discounts,
    CAST(SUM(Order_Profit) * 100.0 / NULLIF(SUM(Sales), 0)
         AS DECIMAL(5,2))                                           AS Profit_Margin_Pct,
    CAST(SUM(Item_Discount) * 100.0 / NULLIF(SUM(Sales), 0)
         AS DECIMAL(5,2))                                           AS Discount_Rate_Pct,
    AVG(Sales)                                                      AS Avg_Order_Value,
    SUM(Item_Quantity)                                              AS Total_Units_Sold
FROM Fact_Orders;
GO

-- 1.2 Sales by Year and Quarter
SELECT
    d.Year,
    d.Quarter,
    COUNT(DISTINCT f.Order_ID)                                      AS Orders,
    SUM(f.Sales)                                                    AS Total_Sales,
    SUM(f.Order_Profit)                                             AS Total_Profit,
    SUM(f.Item_Discount)                                            AS Total_Discounts,
    CAST(SUM(f.Order_Profit) * 100.0 / NULLIF(SUM(f.Sales), 0)
         AS DECIMAL(5,2))                                           AS Profit_Margin_Pct,
    SUM(f.Sales) - LAG(SUM(f.Sales)) OVER (ORDER BY d.Year, d.Quarter) AS Sales_Change,
    CAST((SUM(f.Sales) - LAG(SUM(f.Sales)) OVER (ORDER BY d.Year, d.Quarter))
         * 100.0 / NULLIF(LAG(SUM(f.Sales)) OVER (ORDER BY d.Year, d.Quarter), 0)
         AS DECIMAL(5,2))                                           AS Sales_Growth_Pct
FROM Fact_Orders f
JOIN Dim_Date d ON f.Order_DateKey = d.DateKey
GROUP BY d.Year, d.Quarter
ORDER BY d.Year, d.Quarter;
GO

-- 1.3 Monthly Sales Trend with Running Total
SELECT
    d.Year,
    d.Month_Num,
    d.Month_Name,
    d.Year_Month,
    SUM(f.Sales)                                                    AS Monthly_Sales,
    SUM(f.Order_Profit)                                             AS Monthly_Profit,
    SUM(SUM(f.Sales)) OVER (PARTITION BY d.Year ORDER BY d.Month_Num) AS YTD_Sales,
    AVG(SUM(f.Sales)) OVER (ORDER BY d.Year, d.Month_Num ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS Rolling_3M_Avg
FROM Fact_Orders f
JOIN Dim_Date d ON f.Order_DateKey = d.DateKey
GROUP BY d.Year, d.Month_Num, d.Month_Name, d.Year_Month
ORDER BY d.Year, d.Month_Num;
GO

-- 1.4 Sales by Day of Week
SELECT
    d.Day_of_Week,
    COUNT(DISTINCT f.Order_ID)      AS Orders,
    SUM(f.Sales)                    AS Total_Sales,
    AVG(f.Sales)                    AS Avg_Sales,
    SUM(f.Order_Profit)             AS Total_Profit
FROM Fact_Orders f
JOIN Dim_Date d ON f.Order_DateKey = d.DateKey
GROUP BY d.Day_of_Week
ORDER BY
    CASE d.Day_of_Week
        WHEN 'Monday'    THEN 1
        WHEN 'Tuesday'   THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday'  THEN 4
        WHEN 'Friday'    THEN 5
        WHEN 'Saturday'  THEN 6
        WHEN 'Sunday'    THEN 7
    END;
GO


-- 2.1 Top 20 Products by Revenue
SELECT TOP 20
    p.Product_Name,
    p.Category_Name,
    p.Department_Name,
    p.Price_Range,
    p.Product_Price,
    SUM(f.Item_Quantity)                                            AS Units_Sold,
    SUM(f.Sales)                                                    AS Total_Sales,
    SUM(f.Order_Profit)                                             AS Total_Profit,
    CAST(AVG(f.Item_Profit_Ratio) * 100 AS DECIMAL(5,2))           AS Avg_Profit_Ratio_Pct,
    AVG(f.Item_Discount_Rate)                                       AS Avg_Discount_Rate,
    COUNT(DISTINCT f.Order_ID)                                      AS Order_Count
FROM Fact_Orders f
JOIN Dim_Product p ON f.Product_Card_ID = p.Product_Card_ID
GROUP BY p.Product_Name, p.Category_Name, p.Department_Name,
         p.Price_Range, p.Product_Price
ORDER BY Total_Sales DESC;
GO


-- 2.2 Category Performance
SELECT
    p.Category_Name,
    p.Department_Name,
    COUNT(DISTINCT f.Order_ID)                                      AS Orders,
    SUM(f.Item_Quantity)                                            AS Units_Sold,
    SUM(f.Sales)                                                    AS Total_Sales,
    SUM(f.Order_Profit)                                             AS Total_Profit,
    CAST(SUM(f.Order_Profit) * 100.0 / NULLIF(SUM(f.Sales), 0)
         AS DECIMAL(5,2))                                           AS Profit_Margin_Pct,
    CAST(SUM(f.Sales) * 100.0 /
         SUM(SUM(f.Sales)) OVER () AS DECIMAL(5,2))                AS Sales_Share_Pct
FROM Fact_Orders f
JOIN Dim_Product p ON f.Product_Card_ID = p.Product_Card_ID
GROUP BY p.Category_Name, p.Department_Name
ORDER BY Total_Sales DESC;
GO


-- 2.3 Department Revenue Ranking
SELECT
    p.Department_Name,
    SUM(f.Sales)                                                    AS Total_Sales,
    SUM(f.Order_Profit)                                             AS Total_Profit,
    COUNT(DISTINCT p.Product_Card_ID)                               AS Product_Count,
    SUM(f.Item_Quantity)                                            AS Units_Sold,
    RANK() OVER (ORDER BY SUM(f.Sales) DESC)                       AS Revenue_Rank
FROM Fact_Orders f
JOIN Dim_Product p ON f.Product_Card_ID = p.Product_Card_ID
GROUP BY p.Department_Name
ORDER BY Total_Sales DESC;
GO

-- 2.4 Price Range Analysis
SELECT
    p.Price_Range,
    COUNT(DISTINCT p.Product_Card_ID)                               AS Products,
    SUM(f.Item_Quantity)                                            AS Units_Sold,
    SUM(f.Sales)                                                    AS Total_Sales,
    AVG(f.Sales)                                                    AS Avg_Order_Value,
    CAST(SUM(f.Order_Profit) * 100.0 / NULLIF(SUM(f.Sales), 0)
         AS DECIMAL(5,2))                                           AS Profit_Margin_Pct
FROM Fact_Orders f
JOIN Dim_Product p ON f.Product_Card_ID = p.Product_Card_ID
GROUP BY p.Price_Range
ORDER BY AVG(p.Product_Price);
GO

-- 2.5 Stock Status Impact
SELECT
    p.Stock_Status,
    COUNT(DISTINCT p.Product_Card_ID)   AS Products,
    SUM(f.Sales)                        AS Total_Sales,
    SUM(f.Item_Quantity)                AS Units_Sold,
    AVG(f.Item_Discount_Rate) * 100     AS Avg_Discount_Pct
FROM Fact_Orders f
JOIN Dim_Product p ON f.Product_Card_ID = p.Product_Card_ID
GROUP BY p.Stock_Status;
GO

-- 3.1 Customer Segment Revenue
SELECT
    c.Customer_Segment,
    COUNT(DISTINCT f.Customer_ID)                                   AS Customers,
    COUNT(DISTINCT f.Order_ID)                                      AS Orders,
    SUM(f.Sales)                                                    AS Total_Sales,
    SUM(f.Order_Profit)                                             AS Total_Profit,
    AVG(f.Sales)                                                    AS Avg_Order_Value,
    SUM(f.Sales) / COUNT(DISTINCT f.Customer_ID)                   AS Sales_Per_Customer,
    CAST(SUM(f.Sales) * 100.0 /
         SUM(SUM(f.Sales)) OVER () AS DECIMAL(5,2))                AS Revenue_Share_Pct
FROM Fact_Orders f
JOIN Dim_Customer c ON f.Customer_ID = c.Customer_ID
GROUP BY c.Customer_Segment
ORDER BY Total_Sales DESC;
GO

-- 3.2 Top 20 Customers by Lifetime Value
SELECT TOP 20
    f.Customer_ID,
    c.Customer_Segment,
    c.Customer_City,
    c.Customer_Country,
    c.Market,
    COUNT(DISTINCT f.Order_ID)          AS Total_Orders,
    SUM(f.Sales)                        AS Lifetime_Sales,
    SUM(f.Order_Profit)                 AS Lifetime_Profit,
    AVG(f.Sales)                        AS Avg_Order_Value,
    MIN(f.Order_DateKey)                AS First_Order,
    MAX(f.Order_DateKey)                AS Last_Order,
    DATEDIFF(DAY, MIN(f.Order_DateKey), MAX(f.Order_DateKey)) AS Customer_Lifespan_Days
FROM Fact_Orders f
JOIN Dim_Customer c ON f.Customer_ID = c.Customer_ID
GROUP BY f.Customer_ID, c.Customer_Segment,
         c.Customer_City, c.Customer_Country, c.Market
ORDER BY Lifetime_Sales DESC;
GO

-- 3.3 Customer Segment by Market
SELECT
    c.Market,
    c.Customer_Segment,
    COUNT(DISTINCT f.Customer_ID)   AS Customers,
    SUM(f.Sales)                    AS Total_Sales,
    AVG(f.Sales)                    AS Avg_Order_Value,
    SUM(f.Order_Profit)             AS Total_Profit
FROM Fact_Orders f
JOIN Dim_Customer c ON f.Customer_ID = c.Customer_ID
GROUP BY c.Market, c.Customer_Segment
ORDER BY c.Market, Total_Sales DESC;
GO


-- 3.4 RFM Analysis (Recency, Frequency, Monetary)
WITH RFM AS (
    SELECT
        f.Customer_ID,
        DATEDIFF(DAY, MAX(f.Order_DateKey), '2018-02-28')  AS Recency_Days,
        COUNT(DISTINCT f.Order_ID)                          AS Frequency,
        SUM(f.Sales)                                        AS Monetary
    FROM Fact_Orders f
    GROUP BY f.Customer_ID
),
RFM_Scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY Recency_Days ASC)  AS R_Score,
        NTILE(5) OVER (ORDER BY Frequency DESC)    AS F_Score,
        NTILE(5) OVER (ORDER BY Monetary DESC)     AS M_Score
    FROM RFM
)
SELECT
    Customer_ID,
    Recency_Days,
    Frequency,
    CAST(Monetary AS DECIMAL(12,2))                AS Monetary,
    R_Score,
    F_Score,
    M_Score,
    R_Score + F_Score + M_Score                    AS RFM_Total,
    CASE
        WHEN R_Score >= 4 AND F_Score >= 4 AND M_Score >= 4 THEN 'Champions'
        WHEN R_Score >= 3 AND F_Score >= 3 AND M_Score >= 3 THEN 'Loyal Customers'
        WHEN R_Score >= 4 AND F_Score <= 2             THEN 'New Customers'
        WHEN R_Score <= 2 AND F_Score >= 3             THEN 'At Risk'
        WHEN R_Score = 1 AND F_Score = 1               THEN 'Lost'
        ELSE 'Potential Loyalists'
    END                                            AS RFM_Segment
FROM RFM_Scored
ORDER BY RFM_Total DESC;
GO


-- 4.1 Shipping Mode Performance
SELECT
    o.Shipping_Mode,
    COUNT(*)                                                        AS Total_Shipments,
    AVG(f.Shipping_Days_Actual)                                     AS Avg_Actual_Days,
    AVG(f.Shipping_Days_Scheduled)                                  AS Avg_Scheduled_Days,
    AVG(f.Shipping_Delay_Days)                                      AS Avg_Delay_Days,
    SUM(CAST(f.Late_Delivery_Risk AS INT))                          AS Late_Count,
    CAST(SUM(CAST(f.Late_Delivery_Risk AS INT)) * 100.0
         / COUNT(*) AS DECIMAL(5,2))                                AS Late_Rate_Pct,
    SUM(f.Sales)                                                    AS Total_Sales,
    CAST(SUM(f.Order_Profit) * 100.0 / NULLIF(SUM(f.Sales), 0)
         AS DECIMAL(5,2))                                           AS Profit_Margin_Pct
FROM Fact_Orders f
JOIN Dim_Order o ON f.Order_ID = o.Order_ID
GROUP BY o.Shipping_Mode
ORDER BY Total_Shipments DESC;
GO

-- 4.2 Delivery Status Breakdown
SELECT
    o.Delivery_Status,
    o.Shipping_Mode,
    COUNT(*)                                                        AS Count,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()
         AS DECIMAL(5,2))                                           AS Pct_of_Total,
    AVG(f.Shipping_Delay_Days)                                      AS Avg_Delay,
    SUM(f.Sales)                                                    AS Sales_Affected,
    SUM(f.Order_Profit)                                             AS Profit_Affected
FROM Fact_Orders f
JOIN Dim_Order o ON f.Order_ID = o.Order_ID
GROUP BY o.Delivery_Status, o.Shipping_Mode
ORDER BY Count DESC;
GO

-- 4.3 Late Delivery by Region and Shipping Mode
SELECT
    o.Order_Region,
    o.Shipping_Mode,
    COUNT(*)                                                        AS Total_Orders,
    SUM(CAST(f.Late_Delivery_Risk AS INT))                          AS Late_Orders,
    CAST(SUM(CAST(f.Late_Delivery_Risk AS INT)) * 100.0
         / COUNT(*) AS DECIMAL(5,2))                                AS Late_Rate_Pct,
    AVG(f.Shipping_Delay_Days)                                      AS Avg_Delay_Days
FROM Fact_Orders f
JOIN Dim_Order o ON f.Order_ID = o.Order_ID
GROUP BY o.Order_Region, o.Shipping_Mode
ORDER BY Late_Rate_Pct DESC;
GO

-- 4.4 Shipping Performance Distribution
SELECT
    f.Shipping_Performance,
    COUNT(*)                                                        AS Orders,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()
         AS DECIMAL(5,2))                                           AS Pct,
    AVG(f.Shipping_Delay_Days)                                      AS Avg_Delay,
    SUM(f.Sales)                                                    AS Total_Sales
FROM Fact_Orders f
GROUP BY f.Shipping_Performance
ORDER BY Orders DESC;
GO


-- 5.1 Sales by Market
SELECT
    c.Market,
    COUNT(DISTINCT f.Customer_ID)                                   AS Customers,
    COUNT(DISTINCT f.Order_ID)                                      AS Orders,
    SUM(f.Sales)                                                    AS Total_Sales,
    SUM(f.Order_Profit)                                             AS Total_Profit,
    CAST(SUM(f.Order_Profit) * 100.0 / NULLIF(SUM(f.Sales), 0)
         AS DECIMAL(5,2))                                           AS Profit_Margin_Pct,
    CAST(SUM(f.Sales) * 100.0 /
         SUM(SUM(f.Sales)) OVER () AS DECIMAL(5,2))                AS Market_Share_Pct
FROM Fact_Orders f
JOIN Dim_Customer c ON f.Customer_ID = c.Customer_ID
GROUP BY c.Market
ORDER BY Total_Sales DESC;
GO

-- 5.2 Top 15 Countries by Revenue
SELECT TOP 15
    c.Customer_Country,
    c.Market,
    COUNT(DISTINCT f.Customer_ID)   AS Customers,
    COUNT(DISTINCT f.Order_ID)      AS Orders,
    SUM(f.Sales)                    AS Total_Sales,
    SUM(f.Order_Profit)             AS Total_Profit,
    AVG(f.Sales)                    AS Avg_Order_Value
FROM Fact_Orders f
JOIN Dim_Customer c ON f.Customer_ID = c.Customer_ID
GROUP BY c.Customer_Country, c.Market
ORDER BY Total_Sales DESC;
GO

-- 5.3 Order Region Performance
SELECT
    o.Order_Region,
    COUNT(DISTINCT f.Order_ID)                                      AS Orders,
    SUM(f.Sales)                                                    AS Total_Sales,
    SUM(f.Order_Profit)                                             AS Total_Profit,
    CAST(SUM(f.Order_Profit) * 100.0 / NULLIF(SUM(f.Sales), 0)
         AS DECIMAL(5,2))                                           AS Profit_Margin_Pct,
    SUM(CAST(f.Late_Delivery_Risk AS INT))                          AS Late_Deliveries,
    CAST(SUM(CAST(f.Late_Delivery_Risk AS INT)) * 100.0
         / COUNT(*) AS DECIMAL(5,2))                                AS Late_Rate_Pct,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1 ELSE 0 END)         AS Fraud_Orders
FROM Fact_Orders f
JOIN Dim_Order o ON f.Order_ID = o.Order_ID
GROUP BY o.Order_Region
ORDER BY Total_Sales DESC;
GO

-- 5.4 Market vs Shipping Mode Cross Analysis
SELECT
    c.Market,
    o.Shipping_Mode,
    COUNT(*)                        AS Orders,
    SUM(f.Sales)                    AS Total_Sales,
    CAST(SUM(CAST(f.Late_Delivery_Risk AS INT)) * 100.0
         / COUNT(*) AS DECIMAL(5,2)) AS Late_Rate_Pct
FROM Fact_Orders f
JOIN Dim_Customer c ON f.Customer_ID = c.Customer_ID
JOIN Dim_Order    o ON f.Order_ID    = o.Order_ID
GROUP BY c.Market, o.Shipping_Mode
ORDER BY c.Market, Orders DESC;
GO

-- 6.1 Fraud Overview
SELECT
    f.Is_Fraud,
    COUNT(*)                                                        AS Orders,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER ()
         AS DECIMAL(5,2))                                           AS Pct_of_Total,
    SUM(f.Sales)                                                    AS Revenue_Impact,
    AVG(f.Sales)                                                    AS Avg_Order_Value,
    SUM(f.Order_Profit)                                             AS Profit_Impact
FROM Fact_Orders f
GROUP BY f.Is_Fraud;
GO

-- 6.2 Fraud by Order Status
SELECT
    o.Order_Status,
    o.Status_Group,
    COUNT(*)                                                        AS Total_Orders,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1 ELSE 0 END)         AS Fraud_Count,
    CAST(SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1.0 ELSE 0 END)
         * 100 / COUNT(*) AS DECIMAL(5,2))                         AS Fraud_Rate_Pct,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN f.Sales ELSE 0 END)   AS Fraud_Sales
FROM Fact_Orders f
JOIN Dim_Order o ON f.Order_ID = o.Order_ID
GROUP BY o.Order_Status, o.Status_Group
ORDER BY Fraud_Count DESC;
GO

-- 6.3 Fraud by Region and Market
SELECT
    c.Market,
    o.Order_Region,
    COUNT(*)                                                        AS Total_Orders,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1 ELSE 0 END)         AS Fraud_Orders,
    CAST(SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1.0 ELSE 0 END)
         * 100 / COUNT(*) AS DECIMAL(5,2))                         AS Fraud_Rate_Pct,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN f.Sales ELSE 0 END)   AS Fraud_Revenue
FROM Fact_Orders f
JOIN Dim_Customer c ON f.Customer_ID = c.Customer_ID
JOIN Dim_Order    o ON f.Order_ID    = o.Order_ID
GROUP BY c.Market, o.Order_Region
ORDER BY Fraud_Rate_Pct DESC;
GO

-- 6.4 Fraud Trend Over Time
SELECT
    d.Year,
    d.Quarter,
    COUNT(*)                                                        AS Total_Orders,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1 ELSE 0 END)         AS Fraud_Count,
    CAST(SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1.0 ELSE 0 END)
         * 100 / COUNT(*) AS DECIMAL(5,2))                         AS Fraud_Rate_Pct,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN f.Sales ELSE 0 END)   AS Fraud_Revenue
FROM Fact_Orders f
JOIN Dim_Date d ON f.Order_DateKey = d.DateKey
GROUP BY d.Year, d.Quarter
ORDER BY d.Year, d.Quarter;
GO

-- 6.5 Fraud by Shipping Mode
SELECT
    o.Shipping_Mode,
    COUNT(*)                                                        AS Total_Orders,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1 ELSE 0 END)         AS Fraud_Count,
    CAST(SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1.0 ELSE 0 END)
         * 100 / COUNT(*) AS DECIMAL(5,2))                         AS Fraud_Rate_Pct,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN f.Sales ELSE 0 END)   AS Fraud_Revenue
FROM Fact_Orders f
JOIN Dim_Order o ON f.Order_ID = o.Order_ID
GROUP BY o.Shipping_Mode
ORDER BY Fraud_Rate_Pct DESC;
GO


-- 7.1 Profit Category Breakdown
SELECT
    f.Profit_Category,
    f.Profit_Tier,
    COUNT(*)                                                        AS Orders,
    SUM(f.Sales)                                                    AS Total_Sales,
    SUM(f.Order_Profit)                                             AS Total_Profit,
    AVG(f.Item_Profit_Ratio) * 100                                  AS Avg_Profit_Ratio_Pct
FROM Fact_Orders f
GROUP BY f.Profit_Category, f.Profit_Tier
ORDER BY f.Profit_Category, f.Profit_Tier;
GO

-- 7.2 Discount Impact on Profitability
SELECT
    f.Discount_Tier,
    COUNT(*)                                                        AS Orders,
    AVG(f.Item_Discount_Rate) * 100                                 AS Avg_Discount_Pct,
    SUM(f.Sales)                                                    AS Total_Sales,
    SUM(f.Item_Discount)                                            AS Total_Discount_Amount,
    SUM(f.Order_Profit)                                             AS Total_Profit,
    CAST(SUM(f.Order_Profit) * 100.0 / NULLIF(SUM(f.Sales), 0)
         AS DECIMAL(5,2))                                           AS Profit_Margin_Pct
FROM Fact_Orders f
GROUP BY f.Discount_Tier
ORDER BY AVG(f.Item_Discount_Rate);
GO

-- 7.3 Profit by Category and Discount Tier
SELECT
    p.Category_Name,
    f.Discount_Tier,
    COUNT(*)                                                        AS Orders,
    SUM(f.Sales)                                                    AS Total_Sales,
    SUM(f.Order_Profit)                                             AS Total_Profit,
    CAST(SUM(f.Order_Profit) * 100.0 / NULLIF(SUM(f.Sales), 0)
         AS DECIMAL(5,2))                                           AS Profit_Margin_Pct
FROM Fact_Orders f
JOIN Dim_Product p ON f.Product_Card_ID = p.Product_Card_ID
GROUP BY p.Category_Name, f.Discount_Tier
ORDER BY p.Category_Name, f.Discount_Tier;
GO


-- 7.4 Loss-Making Orders Analysis
SELECT TOP 50
    f.Order_ID,
    f.Order_Item_ID,
    p.Product_Name,
    p.Category_Name,
    o.Order_Region,
    c.Customer_Segment,
    f.Sales,
    f.Order_Profit,
    f.Item_Discount_Rate * 100      AS Discount_Pct,
    f.Item_Profit_Ratio * 100       AS Profit_Ratio_Pct,
    o.Shipping_Mode,
    o.Delivery_Status
FROM Fact_Orders f
JOIN Dim_Product  p ON f.Product_Card_ID = p.Product_Card_ID
JOIN Dim_Order    o ON f.Order_ID        = o.Order_ID
JOIN Dim_Customer c ON f.Customer_ID     = c.Customer_ID
WHERE f.Order_Profit < 0
ORDER BY f.Order_Profit ASC;
GO


-- 8.1 Overall Web Activity
SELECT
    COUNT(*)                                                                    AS Total_Visits,
    SUM(CAST(Is_Add_To_Cart AS INT))                                            AS Add_To_Cart_Events,
    CAST(SUM(CAST(Is_Add_To_Cart AS INT)) * 100.0 / COUNT(*) AS DECIMAL(5,2))  AS Cart_Rate_Pct,
    COUNT(DISTINCT IP_Address)                                                  AS Unique_Visitors,
    COUNT(DISTINCT Product_Name)                                                AS Products_Viewed
FROM Fact_WebLogs;
GO

-- 8.2 Top 20 Viewed Products
SELECT TOP 20
    Product_Name,
    Category_Name,
    COUNT(*)                                                                    AS Total_Views,
    SUM(CAST(Is_Add_To_Cart AS INT))                                            AS Add_To_Cart,
    CAST(SUM(CAST(Is_Add_To_Cart AS INT)) * 100.0 / COUNT(*) AS DECIMAL(5,2))  AS Conversion_Pct
FROM Fact_WebLogs
GROUP BY Product_Name, Category_Name
ORDER BY Total_Views DESC;
GO

-- 8.3 Traffic by Hour Group
SELECT
    Hour_Group,
    COUNT(*)                                                                    AS Visits,
    SUM(CAST(Is_Add_To_Cart AS INT))                                            AS Cart_Events,
    CAST(SUM(CAST(Is_Add_To_Cart AS INT)) * 100.0 / COUNT(*) AS DECIMAL(5,2))  AS Conversion_Pct,
    COUNT(DISTINCT IP_Address)                                                  AS Unique_Visitors
FROM Fact_WebLogs
GROUP BY Hour_Group
ORDER BY Visits DESC;
GO

-- 8.4 Web Activity by Year and Month
SELECT
    Log_Year,
    Log_Month_Num,
    COUNT(*)                                                                    AS Visits,
    SUM(CAST(Is_Add_To_Cart AS INT))                                            AS Cart_Events,
    COUNT(DISTINCT IP_Address)                                                  AS Unique_Visitors,
    CAST(SUM(CAST(Is_Add_To_Cart AS INT)) * 100.0 / COUNT(*) AS DECIMAL(5,2))  AS Conversion_Pct
FROM Fact_WebLogs
GROUP BY Log_Year, Log_Month_Num
ORDER BY Log_Year, Log_Month_Num;
GO

-- 8.5 Product Views vs Actual Sales Correlation
SELECT
    p.Product_Name,
    p.Category_Name,
    COALESCE(w.Total_Views, 0)                                                  AS Web_Views,
    COALESCE(w.Add_To_Cart, 0)                                                  AS Add_To_Cart,
    COALESCE(s.Units_Sold, 0)                                                   AS Units_Sold,
    CAST(COALESCE(s.Total_Sales, 0) AS DECIMAL(14,2))                           AS Total_Sales,
    CASE WHEN COALESCE(w.Total_Views, 0) > 0
         THEN CAST(COALESCE(s.Units_Sold, 0) * 100.0 / w.Total_Views AS DECIMAL(10,2))
         ELSE 0 END                                                             AS View_to_Sale_Pct
FROM Dim_Product p
LEFT JOIN (
    SELECT Product_Name,
           COUNT(*)                         AS Total_Views,
           SUM(CAST(Is_Add_To_Cart AS INT)) AS Add_To_Cart
    FROM Fact_WebLogs
    GROUP BY Product_Name
) w ON p.Product_Name = w.Product_Name
LEFT JOIN (
    SELECT Product_Card_ID,
           SUM(Item_Quantity) AS Units_Sold,
           SUM(Sales)         AS Total_Sales
    FROM Fact_Orders
    GROUP BY Product_Card_ID
) s ON p.Product_Card_ID = s.Product_Card_ID
ORDER BY Web_Views DESC;
GO

-- 9.1 Year-over-Year Comparison
SELECT
    d.Month_Num,
    d.Month_Name,
    SUM(CASE WHEN d.Year = 2015 THEN f.Sales ELSE 0 END)           AS Sales_2015,
    SUM(CASE WHEN d.Year = 2016 THEN f.Sales ELSE 0 END)           AS Sales_2016,
    SUM(CASE WHEN d.Year = 2017 THEN f.Sales ELSE 0 END)           AS Sales_2017,
    SUM(CASE WHEN d.Year = 2018 THEN f.Sales ELSE 0 END)           AS Sales_2018,
    CAST((SUM(CASE WHEN d.Year = 2017 THEN f.Sales ELSE 0 END) -
          SUM(CASE WHEN d.Year = 2016 THEN f.Sales ELSE 0 END))
         * 100.0 / NULLIF(SUM(CASE WHEN d.Year = 2016 THEN f.Sales ELSE 0 END), 0)
         AS DECIMAL(5,2))                                           AS YoY_Growth_2017_Pct
FROM Fact_Orders f
JOIN Dim_Date d ON f.Order_DateKey = d.DateKey
GROUP BY d.Month_Num, d.Month_Name
ORDER BY d.Month_Num;
GO

-- 9.2 Customer Cohort Retention by First Order Year
WITH FirstOrder AS (
    SELECT Customer_ID, MIN(Order_DateKey) AS First_Order_Date
    FROM Fact_Orders
    GROUP BY Customer_ID
),
Cohort AS (
    SELECT
        f.Customer_ID,
        YEAR(fo.First_Order_Date)                                   AS Cohort_Year,
        YEAR(f.Order_DateKey)                                       AS Order_Year,
        YEAR(f.Order_DateKey) - YEAR(fo.First_Order_Date)          AS Year_Number
    FROM Fact_Orders f
    JOIN FirstOrder fo ON f.Customer_ID = fo.Customer_ID
)
SELECT
    Cohort_Year,
    COUNT(DISTINCT CASE WHEN Year_Number = 0 THEN Customer_ID END) AS Year_0,
    COUNT(DISTINCT CASE WHEN Year_Number = 1 THEN Customer_ID END) AS Year_1,
    COUNT(DISTINCT CASE WHEN Year_Number = 2 THEN Customer_ID END) AS Year_2,
    COUNT(DISTINCT CASE WHEN Year_Number = 3 THEN Customer_ID END) AS Year_3
FROM Cohort
GROUP BY Cohort_Year
ORDER BY Cohort_Year;
GO


-- 9.3 Full Order Scorecard (one row per order)
SELECT
    f.Order_ID,
    d_o.Year                                                        AS Order_Year,
    d_o.Quarter,
    d_o.Month_Name,
    o.Order_Status,
    o.Status_Group,
    o.Shipping_Mode,
    o.Delivery_Status,
    o.Order_Region,
    c.Customer_Segment,
    c.Market,
    p.Category_Name,
    p.Department_Name,
    SUM(f.Sales)                                                    AS Order_Sales,
    SUM(f.Order_Profit)                                             AS Order_Profit,
    SUM(f.Item_Quantity)                                            AS Total_Units,
    SUM(f.Item_Discount)                                            AS Total_Discount,
    AVG(f.Shipping_Days_Actual)                                     AS Avg_Ship_Days,
    MAX(CAST(f.Late_Delivery_Risk AS INT))                          AS Has_Late_Risk,
    MAX(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1 ELSE 0 END)         AS Is_Fraud
FROM Fact_Orders f
JOIN Dim_Date     d_o ON f.Order_DateKey    = d_o.DateKey
JOIN Dim_Order    o   ON f.Order_ID         = o.Order_ID
JOIN Dim_Customer c   ON f.Customer_ID      = c.Customer_ID
JOIN Dim_Product  p   ON f.Product_Card_ID  = p.Product_Card_ID
GROUP BY
    f.Order_ID, d_o.Year, d_o.Quarter, d_o.Month_Name,
    o.Order_Status, o.Status_Group, o.Shipping_Mode,
    o.Delivery_Status, o.Order_Region,
    c.Customer_Segment, c.Market,
    p.Category_Name, p.Department_Name
ORDER BY Order_Sales DESC;
GO


USE SupplyChainDW;
GO

-- 10.1 Master Unified View (All Tables Joined)
-- Every order line with full context from all dimensions
SELECT
    f.Order_ID,
    f.Order_Item_ID,

    d.Year                      AS Order_Year,
    d.Quarter                   AS Order_Quarter,
    d.Month_Name                AS Order_Month,
    d.Year_Month,
    d.Day_of_Week,
    d.Is_Weekend,

    c.Customer_Segment,
    c.Market,
    c.Customer_Country,
    c.Customer_City,
    c.Customer_State,

    p.Product_Name,
    p.Category_Name,
    p.Department_Name,
    p.Price_Range,
    p.Stock_Status,

    o.Order_Status,
    o.Status_Group,
    o.Shipping_Mode,
    o.Delivery_Status,
    o.Delivery_Risk_Flag,
    o.Order_Region,
    o.Transaction_Type,

    f.Sales,
    f.Net_Revenue,
    f.Order_Profit,
    f.Item_Quantity,
    f.Item_Discount,
    f.Item_Discount_Rate,
    f.Item_Profit_Ratio,
    f.Item_Total,
    f.Benefit_Per_Order,

    f.Shipping_Days_Actual,
    f.Shipping_Days_Scheduled,
    f.Shipping_Delay_Days,
    f.Shipping_Performance,
    f.Late_Delivery_Risk,

    f.Is_Fraud,
    f.Profit_Category,
    f.Profit_Tier,
    f.Discount_Tier

FROM Fact_Orders     f
JOIN Dim_Date        d ON f.Order_DateKey    = d.DateKey
JOIN Dim_Customer    c ON f.Customer_ID      = c.Customer_ID
JOIN Dim_Product     p ON f.Product_Card_ID  = p.Product_Card_ID
JOIN Dim_Order       o ON f.Order_ID         = o.Order_ID
ORDER BY f.Order_DateKey, f.Order_ID;
GO


-- 10.2 Revenue by Segment + Market + Category + Year
SELECT
    d.Year,
    d.Quarter,
    c.Market,
    c.Customer_Segment,
    p.Department_Name,
    p.Category_Name,
    p.Price_Range,
    o.Shipping_Mode,
    o.Order_Region,
    COUNT(DISTINCT f.Order_ID)                                          AS Orders,
    COUNT(DISTINCT f.Customer_ID)                                       AS Customers,
    SUM(f.Item_Quantity)                                                AS Units_Sold,
    SUM(f.Sales)                                                        AS Total_Sales,
    SUM(f.Net_Revenue)                                                  AS Net_Revenue,
    SUM(f.Order_Profit)                                                 AS Total_Profit,
    SUM(f.Item_Discount)                                                AS Discounts_Given,
    CAST(SUM(f.Order_Profit) * 100.0 / NULLIF(SUM(f.Sales), 0)
         AS DECIMAL(5,2))                                               AS Profit_Margin_Pct,
    SUM(CAST(f.Late_Delivery_Risk AS INT))                              AS Late_Deliveries,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1 ELSE 0 END)             AS Fraud_Count
FROM Fact_Orders     f
JOIN Dim_Date        d ON f.Order_DateKey    = d.DateKey
JOIN Dim_Customer    c ON f.Customer_ID      = c.Customer_ID
JOIN Dim_Product     p ON f.Product_Card_ID  = p.Product_Card_ID
JOIN Dim_Order       o ON f.Order_ID         = o.Order_ID
GROUP BY
    d.Year, d.Quarter, c.Market, c.Customer_Segment,
    p.Department_Name, p.Category_Name, p.Price_Range,
    o.Shipping_Mode, o.Order_Region
ORDER BY Total_Sales DESC;
GO


-- 10.3 Fraud vs Legitimate Orders — Full Profile
SELECT
    f.Is_Fraud,
    d.Year,
    d.Quarter,
    c.Market,
    c.Customer_Segment,
    o.Shipping_Mode,
    o.Order_Region,
    o.Status_Group,
    p.Department_Name,
    COUNT(*)                                                            AS Order_Lines,
    COUNT(DISTINCT f.Order_ID)                                         AS Unique_Orders,
    SUM(f.Sales)                                                        AS Total_Sales,
    SUM(f.Order_Profit)                                                 AS Total_Profit,
    AVG(f.Sales)                                                        AS Avg_Order_Value,
    AVG(f.Shipping_Delay_Days)                                          AS Avg_Delay_Days,
    SUM(CAST(f.Late_Delivery_Risk AS INT))                              AS Late_Count
FROM Fact_Orders     f
JOIN Dim_Date        d ON f.Order_DateKey    = d.DateKey
JOIN Dim_Customer    c ON f.Customer_ID      = c.Customer_ID
JOIN Dim_Product     p ON f.Product_Card_ID  = p.Product_Card_ID
JOIN Dim_Order       o ON f.Order_ID         = o.Order_ID
GROUP BY
    f.Is_Fraud, d.Year, d.Quarter, c.Market,
    c.Customer_Segment, o.Shipping_Mode, o.Order_Region,
    o.Status_Group, p.Department_Name
ORDER BY f.Is_Fraud, Total_Sales DESC;
GO


-- 10.4 Shipping Performance by Market + Category + Segment
SELECT
    c.Market,
    c.Customer_Segment,
    p.Category_Name,
    o.Shipping_Mode,
    o.Delivery_Status,
    f.Shipping_Performance,
    COUNT(*)                                                            AS Shipments,
    AVG(f.Shipping_Days_Actual)                                         AS Avg_Actual_Days,
    AVG(f.Shipping_Delay_Days)                                          AS Avg_Delay,
    SUM(CAST(f.Late_Delivery_Risk AS INT))                              AS Late_Count,
    CAST(SUM(CAST(f.Late_Delivery_Risk AS INT)) * 100.0
         / COUNT(*) AS DECIMAL(5,2))                                    AS Late_Rate_Pct,
    SUM(f.Sales)                                                        AS Sales_At_Risk
FROM Fact_Orders     f
JOIN Dim_Customer    c ON f.Customer_ID      = c.Customer_ID
JOIN Dim_Product     p ON f.Product_Card_ID  = p.Product_Card_ID
JOIN Dim_Order       o ON f.Order_ID         = o.Order_ID
GROUP BY
    c.Market, c.Customer_Segment, p.Category_Name,
    o.Shipping_Mode, o.Delivery_Status, f.Shipping_Performance
ORDER BY Late_Rate_Pct DESC;
GO


-- 10.5 Monthly Trend — Sales + Profit + Fraud + Late Delivery (All Linked)
SELECT
    d.Year,
    d.Month_Num,
    d.Month_Name,
    d.Year_Month,
    COUNT(DISTINCT f.Order_ID)                                          AS Orders,
    COUNT(DISTINCT f.Customer_ID)                                       AS Active_Customers,
    SUM(f.Sales)                                                        AS Total_Sales,
    SUM(f.Order_Profit)                                                 AS Total_Profit,
    SUM(f.Item_Discount)                                                AS Total_Discounts,
    CAST(SUM(f.Order_Profit) * 100.0 / NULLIF(SUM(f.Sales), 0)
         AS DECIMAL(5,2))                                               AS Profit_Margin_Pct,
    SUM(CAST(f.Late_Delivery_Risk AS INT))                              AS Late_Deliveries,
    CAST(SUM(CAST(f.Late_Delivery_Risk AS INT)) * 100.0
         / COUNT(*) AS DECIMAL(5,2))                                    AS Late_Rate_Pct,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1 ELSE 0 END)             AS Fraud_Orders,
    CAST(SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1.0 ELSE 0 END)
         * 100 / COUNT(*) AS DECIMAL(5,2))                              AS Fraud_Rate_Pct,
    SUM(CASE WHEN f.Profit_Category = 'Loss' THEN 1 ELSE 0 END)       AS Loss_Orders,
    SUM(SUM(f.Sales)) OVER (
        PARTITION BY d.Year ORDER BY d.Month_Num)                       AS YTD_Sales
FROM Fact_Orders     f
JOIN Dim_Date        d ON f.Order_DateKey = d.DateKey
GROUP BY d.Year, d.Month_Num, d.Month_Name, d.Year_Month
ORDER BY d.Year, d.Month_Num;
GO

-- 10.6 Product Performance Across All Dimensions
SELECT
    p.Department_Name,
    p.Category_Name,
    p.Product_Name,
    p.Price_Range,
    p.Stock_Status,
    c.Market,
    c.Customer_Segment,
    d.Year,
    o.Shipping_Mode,
    COUNT(DISTINCT f.Order_ID)                                          AS Orders,
    SUM(f.Item_Quantity)                                                AS Units_Sold,
    SUM(f.Sales)                                                        AS Total_Sales,
    SUM(f.Order_Profit)                                                 AS Total_Profit,
    CAST(AVG(f.Item_Profit_Ratio) * 100 AS DECIMAL(5,2))               AS Avg_Profit_Ratio_Pct,
    AVG(f.Item_Discount_Rate) * 100                                     AS Avg_Discount_Pct,
    SUM(CAST(f.Late_Delivery_Risk AS INT))                              AS Late_Deliveries,
    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1 ELSE 0 END)             AS Fraud_Orders
FROM Fact_Orders     f
JOIN Dim_Date        d ON f.Order_DateKey    = d.DateKey
JOIN Dim_Customer    c ON f.Customer_ID      = c.Customer_ID
JOIN Dim_Product     p ON f.Product_Card_ID  = p.Product_Card_ID
JOIN Dim_Order       o ON f.Order_ID         = o.Order_ID
GROUP BY
    p.Department_Name, p.Category_Name, p.Product_Name,
    p.Price_Range, p.Stock_Status, c.Market,
    c.Customer_Segment, d.Year, o.Shipping_Mode
ORDER BY Total_Sales DESC;
GO


-- 10.7 Web Logs + Sales Cross Analysis
-- Which products were browsed AND bought, and how profitable were they?
SELECT
    p.Product_Name,
    p.Category_Name,
    p.Department_Name,
    p.Price_Range,

    COALESCE(w.Total_Views, 0)                                          AS Web_Views,
    COALESCE(w.Cart_Events, 0)                                          AS Cart_Events,
    CAST(COALESCE(w.Cart_Events, 0) * 100.0
         / NULLIF(w.Total_Views, 0) AS DECIMAL(5,2))                   AS Cart_Rate_Pct,

    COALESCE(s.Orders, 0)                                               AS Orders,
    COALESCE(s.Units_Sold, 0)                                           AS Units_Sold,
    CAST(COALESCE(s.Total_Sales, 0) AS DECIMAL(14,2))                  AS Total_Sales,
    CAST(COALESCE(s.Total_Profit, 0) AS DECIMAL(14,2))                 AS Total_Profit,
    CAST(COALESCE(s.Avg_Profit_Ratio, 0) * 100 AS DECIMAL(5,2))        AS Avg_Profit_Ratio_Pct,
    CAST(COALESCE(s.Fraud_Rate, 0) AS DECIMAL(5,2))                    AS Fraud_Rate_Pct,
    CAST(COALESCE(s.Late_Rate, 0) AS DECIMAL(5,2))                     AS Late_Delivery_Rate_Pct,

    CASE
        WHEN COALESCE(w.Total_Views, 0) > 0 AND COALESCE(s.Units_Sold, 0) > 0
             THEN 'Browsed and Bought'
        WHEN COALESCE(w.Total_Views, 0) > 0 AND COALESCE(s.Units_Sold, 0) = 0
             THEN 'Browsed Only'
        WHEN COALESCE(w.Total_Views, 0) = 0 AND COALESCE(s.Units_Sold, 0) > 0
             THEN 'Bought Without Browse'
        ELSE 'No Activity'
    END                                                                 AS Engagement_Type

FROM Dim_Product p

LEFT JOIN (
    SELECT
        Product_Name,
        COUNT(*)                            AS Total_Views,
        SUM(CAST(Is_Add_To_Cart AS INT))    AS Cart_Events
    FROM Fact_WebLogs
    GROUP BY Product_Name
) w ON p.Product_Name = w.Product_Name

LEFT JOIN (
    SELECT
        f.Product_Card_ID,
        COUNT(DISTINCT f.Order_ID)                                              AS Orders,
        SUM(f.Item_Quantity)                                                    AS Units_Sold,
        SUM(f.Sales)                                                            AS Total_Sales,
        SUM(f.Order_Profit)                                                     AS Total_Profit,
        AVG(f.Item_Profit_Ratio)                                                AS Avg_Profit_Ratio,
        SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1.0 ELSE 0 END) * 100
            / NULLIF(COUNT(*), 0)                                               AS Fraud_Rate,
        SUM(CAST(f.Late_Delivery_Risk AS INT)) * 100.0
            / NULLIF(COUNT(*), 0)                                               AS Late_Rate
    FROM Fact_Orders f
    GROUP BY f.Product_Card_ID
) s ON p.Product_Card_ID = s.Product_Card_ID

ORDER BY Web_Views DESC;
GO


-- 10.8 Customer 360 View — Sales + Shipping + Fraud + Web Activity
SELECT
    c.Customer_ID,
    c.Customer_Segment,
    c.Market,
    c.Customer_Country,
    c.Customer_City,

    COUNT(DISTINCT f.Order_ID)                                          AS Total_Orders,
    SUM(f.Sales)                                                        AS Lifetime_Sales,
    SUM(f.Order_Profit)                                                 AS Lifetime_Profit,
    AVG(f.Sales)                                                        AS Avg_Order_Value,
    SUM(f.Item_Quantity)                                                AS Total_Units,
    SUM(f.Item_Discount)                                                AS Total_Discounts_Received,

    MIN(f.Order_DateKey)                                                AS First_Order_Date,
    MAX(f.Order_DateKey)                                                AS Last_Order_Date,
    DATEDIFF(DAY, MIN(f.Order_DateKey), MAX(f.Order_DateKey))          AS Customer_Lifespan_Days,

    SUM(CAST(f.Late_Delivery_Risk AS INT))                              AS Late_Deliveries,
    CAST(SUM(CAST(f.Late_Delivery_Risk AS INT)) * 100.0
         / NULLIF(COUNT(*), 0) AS DECIMAL(5,2))                         AS Late_Rate_Pct,

    SUM(CASE WHEN f.Is_Fraud = 'Fraud' THEN 1 ELSE 0 END)             AS Fraud_Orders,
    SUM(CASE WHEN f.Profit_Category = 'Loss' THEN 1 ELSE 0 END)       AS Loss_Orders,

    COUNT(DISTINCT p.Category_Name)                                     AS Unique_Categories_Bought,
    COUNT(DISTINCT o.Shipping_Mode)                                     AS Shipping_Modes_Used,

    COALESCE(w.Web_Visits, 0)                                           AS Web_Visits,
    COALESCE(w.Web_Cart_Events, 0)                                      AS Web_Cart_Events

FROM Fact_Orders     f
JOIN Dim_Customer    c ON f.Customer_ID      = c.Customer_ID
JOIN Dim_Product     p ON f.Product_Card_ID  = p.Product_Card_ID
JOIN Dim_Order       o ON f.Order_ID         = o.Order_ID

LEFT JOIN (
    SELECT
        IP_Address,
        COUNT(*)                            AS Web_Visits,
        SUM(CAST(Is_Add_To_Cart AS INT))    AS Web_Cart_Events
    FROM Fact_WebLogs
    GROUP BY IP_Address
) w ON CAST(c.Customer_ID AS VARCHAR) = w.IP_Address

GROUP BY
    c.Customer_ID, c.Customer_Segment, c.Market,
    c.Customer_Country, c.Customer_City,
    w.Web_Visits, w.Web_Cart_Events
ORDER BY Lifetime_Sales DESC;
GO