import pandas as pd
import pyodbc
import numpy as np

conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;"
    "DATABASE=SupplyChainDW;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.fast_executemany = True

file = r"D:\SMART-Supply-Chain-Insights\SupplyChain_Cleaned_Master.xlsx"

print("=" * 60)
print("  SMART Supply Chain - SQL Server Loader")
print("=" * 60)

print("\nClearing tables...")
cursor.execute("DELETE FROM dbo.Fact_Orders")
cursor.execute("DELETE FROM dbo.Fact_WebLogs")
cursor.execute("DELETE FROM dbo.Dim_Order")
cursor.execute("DELETE FROM dbo.Dim_Product")
cursor.execute("DELETE FROM dbo.Dim_Customer")
cursor.execute("DELETE FROM dbo.Dim_Date")
conn.commit()
print("Tables cleared")

def insert_df(table, df):
    df = df.replace({np.nan: None})
    cols         = ",".join(df.columns)
    placeholders = ",".join(["?"] * len(df.columns))
    sql          = f"INSERT INTO dbo.{table} ({cols}) VALUES ({placeholders})"
    cursor.executemany(sql, df.values.tolist())
    conn.commit()
    print(f"{table}: {len(df):,} rows loaded")

print("\nReading Excel file (this may take a minute)...")
sheets = pd.read_excel(file, sheet_name=None, engine="openpyxl")
print(f"Sheets found: {list(sheets.keys())}\n")

print("[1/6] Loading Dim_Date...")
df = sheets["Dim_Date"].copy()
df = df.rename(columns={"Date": "DateKey"})
df["DateKey"] = pd.to_datetime(df["DateKey"]).dt.date
insert_df("Dim_Date", df)

print("[2/6] Loading Dim_Customer...")
df = sheets["Dim_Customer"].copy()
insert_df("Dim_Customer", df)

print("[3/6] Loading Dim_Product...")
df = sheets["Dim_Product"].copy()
df = df.drop(columns=[c for c in df.columns if c.lower() == "product_category_id"], errors="ignore")
insert_df("Dim_Product", df)

print("[4/6] Loading Dim_Order...")
df = sheets["Dim_Order"].copy()
df = df.rename(columns={"type": "Transaction_Type"})
df = df.drop(columns=[c for c in df.columns if c.lower() == "order_customer_id"], errors="ignore")
insert_df("Dim_Order", df)

print("[5/6] Loading Fact_Orders...")
df = sheets["Fact_Orders"].copy()
df = df.rename(columns={
    "order_date_dateorders":       "Order_DateKey",
    "shipping_date_dateorders":    "Shipping_DateKey",
    "order_profit_per_order":      "Order_Profit",
    "order_item_quantity":         "Item_Quantity",
    "order_item_discount":         "Item_Discount",
    "order_item_discount_rate":    "Item_Discount_Rate",
    "order_item_product_price":    "Item_Product_Price",
    "order_item_profit_ratio":     "Item_Profit_Ratio",
    "order_item_total":            "Item_Total",
    "days_for_shipping_real":      "Shipping_Days_Actual",
    "days_for_shipment_scheduled": "Shipping_Days_Scheduled",
})
df["Order_DateKey"]    = pd.to_datetime(df["Order_DateKey"]).dt.date
df["Shipping_DateKey"] = pd.to_datetime(df["Shipping_DateKey"]).dt.date
df = df.drop(columns=[c for c in df.columns if c.lower() == "fact_id"], errors="ignore")
insert_df("Fact_Orders", df)

print("[6/6] Loading Fact_WebLogs...")
df = sheets["Web_Access_Logs"].copy()
df = df.rename(columns={
    "product":   "Product_Name",
    "category":  "Category_Name",
    "ip":        "IP_Address",
    "month_num": "Log_Month_Num",
    "date":      "Log_Date",
    "year":      "Log_Year",
    "day":       "Log_Day",
    "hour":      "Log_Hour",
})
df["Log_Date"] = pd.to_datetime(df["Log_Date"], errors="coerce")
df = df.drop(columns=[c for c in df.columns if c.lower() in ("log_id", "month")], errors="ignore")
insert_df("Fact_WebLogs", df)

print("\n" + "=" * 60)
print("  Verification")
print("=" * 60)
cursor.execute("""
    SELECT 'Dim_Date'     , COUNT(*) FROM Dim_Date      UNION ALL
    SELECT 'Dim_Customer' , COUNT(*) FROM Dim_Customer  UNION ALL
    SELECT 'Dim_Product'  , COUNT(*) FROM Dim_Product   UNION ALL
    SELECT 'Dim_Order'    , COUNT(*) FROM Dim_Order     UNION ALL
    SELECT 'Fact_Orders'  , COUNT(*) FROM Fact_Orders   UNION ALL
    SELECT 'Fact_WebLogs' , COUNT(*) FROM Fact_WebLogs
""")
for row in cursor.fetchall():
    print(f"  {row[0]:<20} {row[1]:>10,} rows")

cursor.close()
conn.close()
print("\nDone! All tables loaded successfully.")
print("=" * 60)
