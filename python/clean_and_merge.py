import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")

BASE_DIR = r"D:\SMART-Supply-Chain-Insights"

SUPPLY_CHAIN_FILE = os.path.join(BASE_DIR, "DataCoSupplyChainDataset.csv")
ACCESS_LOGS_FILE  = os.path.join(BASE_DIR, "tokenized_access_logs.csv")
DESCRIPTION_FILE  = os.path.join(BASE_DIR, "DescriptionDataCoSupplyChain.csv")
OUTPUT_FILE       = os.path.join(BASE_DIR, "SupplyChain_Cleaned_Master.xlsx")

print("=" * 60)
print("  SMART Supply Chain - Data Cleaning Pipeline")
print("=" * 60)

print("\n[1/7] Loading supply chain data...")

encodings_to_try = ["latin-1", "iso-8859-1", "cp1252", "utf-8"]
df_supply = None
for enc in encodings_to_try:
    try:
        df_supply = pd.read_csv(SUPPLY_CHAIN_FILE, encoding=enc, low_memory=False)
        print(f"     Loaded with encoding: {enc}")
        print(f"     Shape: {df_supply.shape[0]:,} rows x {df_supply.shape[1]} columns")
        break
    except Exception as e:
        print(f"     Failed with {enc}: {e}")

if df_supply is None:
    print("     Error: Could not load the main file.")
    exit(1)

print("\n[2/7] Cleaning supply chain data...")

df = df_supply.copy()

cols_to_drop = [
    "Customer Email", "Customer Password",
    "Product Description", "Product Image",
    "Customer Street", "Customer Zipcode",
    "Order Item Cardprod Id"
]
df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
print(f"     Dropped {len([c for c in cols_to_drop if c in df_supply.columns])} unnecessary columns")

date_cols = ["order date (DateOrders)", "shipping date (DateOrders)"]
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

before = len(df)
df.drop_duplicates(inplace=True)
print(f"     Removed {before - len(df):,} duplicate rows")

df.columns = (
    df.columns
      .str.strip()
      .str.replace(r"\s+", "_", regex=True)
      .str.replace(r"[^\w]", "", regex=True)
      .str.lower()
)

order_date_col = "order_date_dateorders"
ship_date_col  = "shipping_date_dateorders"

for col in [order_date_col, ship_date_col]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
        mode_val = df[col].mode()
        if len(mode_val) > 0:
            df[col] = df[col].fillna(mode_val[0])

int_cols = [
    "category_id", "customer_id", "department_id",
    "order_id", "order_item_id", "product_card_id",
    "order_item_quantity", "late_delivery_risk",
    "product_status", "order_customer_id", "product_category_id"
]
for col in int_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

float_cols = [
    "benefit_per_order", "sales_per_customer", "order_item_discount",
    "order_item_discount_rate", "order_item_product_price",
    "order_item_profit_ratio", "sales", "order_item_total",
    "order_profit_per_order", "product_price", "latitude", "longitude"
]
for col in float_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).round(4)

text_cols = df.select_dtypes(include=["object"]).columns.tolist()
for col in text_cols:
    df[col] = df[col].fillna("Unknown").astype(str).str.strip()
    df[col] = df[col].replace({"nan": "Unknown", "": "Unknown", "none": "Unknown", "None": "Unknown"})

remaining_num = df.select_dtypes(include=[np.number]).columns.tolist()
df[remaining_num] = df[remaining_num].fillna(0)

if order_date_col in df.columns:
    df["order_year"]        = df[order_date_col].dt.year.fillna(0).astype(int)
    df["order_month"]       = df[order_date_col].dt.month.fillna(0).astype(int)
    df["order_month_name"]  = df[order_date_col].dt.strftime("%B").fillna("Unknown")
    df["order_quarter"]     = df[order_date_col].dt.quarter.map({1:"Q1",2:"Q2",3:"Q3",4:"Q4"}).fillna("Unknown")
    df["order_day_of_week"] = df[order_date_col].dt.day_name().fillna("Unknown")
    df["order_week_number"] = df[order_date_col].dt.isocalendar().week.astype("Int64").fillna(0).astype(int)

if "days_for_shipping_real" in df.columns and "days_for_shipment_scheduled" in df.columns:
    df["shipping_delay_days"]  = (df["days_for_shipping_real"] - df["days_for_shipment_scheduled"]).fillna(0).astype(int)
    df["shipping_performance"] = df["shipping_delay_days"].apply(
        lambda x: "Early" if x < 0 else ("On Time" if x == 0 else "Late")
    )

if "order_status" in df.columns:
    df["is_fraud"] = df["order_status"].apply(
        lambda x: "Fraud" if str(x).upper() == "SUSPECTED_FRAUD" else "Legitimate"
    )

if "order_item_profit_ratio" in df.columns:
    df["profit_category"] = df["order_item_profit_ratio"].apply(
        lambda x: "High Profit" if x > 0.2 else ("Low Profit" if x > 0 else "Loss")
    )
    df["profit_tier"] = df["order_item_profit_ratio"].apply(
        lambda x: "High" if x > 0.3 else ("Medium" if x > 0.1 else ("Low" if x > 0 else "Loss"))
    )

if "order_item_discount_rate" in df.columns:
    df["discount_tier"] = df["order_item_discount_rate"].apply(
        lambda x: "No Discount" if x == 0 else (
            "Low (1-10%)" if x <= 0.1 else (
                "Medium (11-20%)" if x <= 0.2 else "High (>20%)"
            )
        )
    )

if "sales" in df.columns and "order_item_discount" in df.columns:
    df["net_revenue"] = (df["sales"] - df["order_item_discount"]).fillna(0).round(4)

for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].fillna("Unknown").replace({"nan": "Unknown", "": "Unknown"})
for col in df.select_dtypes(include=[np.number]).columns:
    df[col] = df[col].fillna(0)

total_null = df.isnull().sum().sum()
print(f"     Null values remaining in main data: {total_null}")
print(f"     Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

print("\n[3/7] Loading and cleaning access logs...")

try:
    df_logs = pd.read_csv(ACCESS_LOGS_FILE, encoding="utf-8", low_memory=False)
    print(f"     Original shape: {df_logs.shape[0]:,} rows x {df_logs.shape[1]} columns")

    df_logs.drop_duplicates(inplace=True)
    df_logs.dropna(subset=["Product", "Category", "Date"], inplace=True)

    df_logs["Date"]      = pd.to_datetime(df_logs["Date"], errors="coerce")
    df_logs.dropna(subset=["Date"], inplace=True)

    df_logs["Year"]      = df_logs["Date"].dt.year.astype(int)
    df_logs["Month_Num"] = df_logs["Date"].dt.month.astype(int)
    df_logs["Day"]       = df_logs["Date"].dt.day.astype(int)
    df_logs["Hour"]      = pd.to_numeric(df_logs["Hour"], errors="coerce").fillna(0).astype(int)

    for col in df_logs.select_dtypes(include=["object"]).columns:
        df_logs[col] = df_logs[col].fillna("Unknown").astype(str).str.strip()
        df_logs[col] = df_logs[col].replace({"nan": "Unknown", "": "Unknown"})

    df_logs["is_add_to_cart"] = df_logs["url"].str.contains("add_to_cart", na=False).astype(int)
    df_logs["action_type"]    = df_logs["is_add_to_cart"].apply(
        lambda x: "Add to Cart" if x == 1 else "Product View"
    )
    df_logs["hour_group"] = df_logs["Hour"].apply(
        lambda h: "Night (0-5)" if h < 6 else (
            "Morning (6-11)" if h < 12 else (
                "Afternoon (12-17)" if h < 18 else "Evening (18-23)"
            )
        )
    )

    df_logs.columns = df_logs.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)

    for col in df_logs.select_dtypes(include=["object"]).columns:
        df_logs[col] = df_logs[col].fillna("Unknown").replace({"nan": "Unknown", "": "Unknown"})
    for col in df_logs.select_dtypes(include=[np.number]).columns:
        df_logs[col] = df_logs[col].fillna(0)

    logs_null = df_logs.isnull().sum().sum()
    print(f"     Null values remaining in logs: {logs_null}")
    print(f"     Cleaned shape: {df_logs.shape[0]:,} rows x {df_logs.shape[1]} columns")

except Exception as e:
    print(f"     Warning: Could not load access logs - {e}")
    df_logs = pd.DataFrame()

print("\n[4/7] Loading and processing data dictionary...")

FIELD_TO_TABLE = {
    "Type":                         "Dim_Order",
    "Days for shipping (real)":     "Fact_Orders",
    "Days for shipment (scheduled)":"Fact_Orders",
    "Benefit per order":            "Fact_Orders",
    "Sales per customer":           "Fact_Orders",
    "Delivery Status":              "Dim_Order",
    "Late_delivery_risk":           "Fact_Orders",
    "Category Id":                  "Dim_Product",
    "Category Name":                "Dim_Product",
    "Customer City":                "Dim_Customer",
    "Customer Country":             "Dim_Customer",
    "Customer Email":               "Dropped",
    "Customer Fname":               "Dim_Customer",
    "Customer Id":                  "Dim_Customer",
    "Customer Lname":               "Dim_Customer",
    "Customer Password":            "Dropped",
    "Customer Segment":             "Dim_Customer",
    "Customer State":               "Dim_Customer",
    "Customer Street":              "Dropped",
    "Customer Zipcode":             "Dropped",
    "Department Id":                "Dim_Product",
    "Department Name":              "Dim_Product",
    "Latitude":                     "Dim_Customer",
    "Longitude":                    "Dim_Customer",
    "Market":                       "Dim_Customer",
    "Order City":                   "Dim_Order",
    "Order Country":                "Dim_Order",
    "Order Customer Id":            "Dim_Order",
    "order date (DateOrders)":      "Fact_Orders",
    "Order Id":                     "Fact_Orders",
    "Order Item Cardprod Id":       "Dropped",
    "Order Item Discount":          "Fact_Orders",
    "Order Item Discount Rate":     "Fact_Orders",
    "Order Item Id":                "Fact_Orders",
    "Order Item Product Price":     "Fact_Orders",
    "Order Item Profit Ratio":      "Fact_Orders",
    "Order Item Quantity":          "Fact_Orders",
    "Sales":                        "Fact_Orders",
    "Order Item Total":             "Fact_Orders",
    "Order Profit Per Order":       "Fact_Orders",
    "Order Region":                 "Dim_Order",
    "Order State":                  "Dim_Order",
    "Order Status":                 "Dim_Order",
    "Product Card Id":              "Dim_Product",
    "Product Category Id":          "Dim_Product",
    "Product Description":          "Dropped",
    "Product Image":                "Dropped",
    "Product Name":                 "Dim_Product",
    "Product Price":                "Dim_Product",
    "Product Status":               "Dim_Product",
    "Shipping date (DateOrders)":   "Fact_Orders",
    "Shipping Mode":                "Dim_Order",
}

DERIVED_FIELDS = [
    {"Field": "order_year",            "Description": "Year extracted from order date",                         "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "order_month",           "Description": "Month number extracted from order date",                 "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "order_month_name",      "Description": "Month name extracted from order date",                   "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "order_quarter",         "Description": "Quarter (Q1-Q4) from order date",                       "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "order_day_of_week",     "Description": "Day of week from order date",                           "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "order_week_number",     "Description": "ISO week number from order date",                       "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "shipping_delay_days",   "Description": "Actual shipping days minus scheduled days",             "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "shipping_performance",  "Description": "Early / On Time / Late based on delay days",           "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "is_fraud",              "Description": "Fraud / Legitimate based on order status",              "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "profit_category",       "Description": "High Profit / Low Profit / Loss based on profit ratio", "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "profit_tier",           "Description": "High / Medium / Low / Loss (finer profit buckets)",     "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "discount_tier",         "Description": "No Discount / Low / Medium / High discount bands",      "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "net_revenue",           "Description": "Sales minus Order Item Discount",                       "Source": "Derived", "Table": "Fact_Orders"},
    {"Field": "stock_status",          "Description": "In Stock / Out of Stock from product_status flag",      "Source": "Derived", "Table": "Dim_Product"},
    {"Field": "price_range",           "Description": "Budget / Mid / Premium / Luxury price bucket",          "Source": "Derived", "Table": "Dim_Product"},
    {"Field": "status_group",          "Description": "Completed / Cancelled / Fraud / Pending / Other",       "Source": "Derived", "Table": "Dim_Order"},
    {"Field": "delivery_risk_flag",    "Description": "At Risk / Normal based on delivery status",             "Source": "Derived", "Table": "Dim_Order"},
    {"Field": "customer_full_location","Description": "Concatenation of customer city and country",            "Source": "Derived", "Table": "Dim_Customer"},
    {"Field": "is_add_to_cart",        "Description": "1 if URL contains add_to_cart, 0 otherwise",           "Source": "Derived", "Table": "Web_Access_Logs"},
    {"Field": "action_type",           "Description": "Add to Cart / Product View",                           "Source": "Derived", "Table": "Web_Access_Logs"},
    {"Field": "hour_group",            "Description": "Night / Morning / Afternoon / Evening time band",       "Source": "Derived", "Table": "Web_Access_Logs"},
]

try:
    df_desc = pd.read_csv(DESCRIPTION_FILE, encoding="utf-8", header=0)
    df_desc.columns = ["Field", "Description"]
    df_desc["Field"]       = df_desc["Field"].fillna("Unknown").str.strip()
    df_desc["Description"] = df_desc["Description"].fillna("No description").str.strip().str.lstrip(":").str.strip()
    df_desc["Source"]      = "Original"
    df_desc["Table"]       = df_desc["Field"].map(FIELD_TO_TABLE).fillna("Unknown")
    df_desc["Standardized_Column_Name"] = (
        df_desc["Field"]
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^\w]", "", regex=True)
        .str.lower()
    )
    df_derived = pd.DataFrame(DERIVED_FIELDS)
    df_derived["Standardized_Column_Name"] = df_derived["Field"]
    df_data_dict = pd.concat([df_desc, df_derived], ignore_index=True)
    df_data_dict = df_data_dict[["Field", "Standardized_Column_Name", "Description", "Source", "Table"]]
    df_data_dict = df_data_dict.fillna("Unknown")
    df_data_dict.sort_values(["Table", "Field"], inplace=True)
    df_data_dict.reset_index(drop=True, inplace=True)
    print(f"     Data dictionary loaded: {len(df_data_dict)} fields ({len(df_desc)} original + {len(df_derived)} derived)")
except Exception as e:
    print(f"     Warning: Could not load description file - {e}")
    df_data_dict = pd.DataFrame()

print("\n[5/7] Building Star Schema tables...")

def clean_df(frame):
    for col in frame.select_dtypes(include=["object"]).columns:
        frame[col] = frame[col].fillna("Unknown").astype(str).str.strip()
        frame[col] = frame[col].replace({"nan": "Unknown", "": "Unknown", "NaT": "Unknown", "none": "Unknown"})
    for col in frame.select_dtypes(include=[np.number]).columns:
        frame[col] = frame[col].fillna(0)
    for col in frame.select_dtypes(include=["datetime64[ns]"]).columns:
        frame[col] = frame[col].fillna(pd.Timestamp("2015-01-01"))
    return frame

fact_cols = [
    "order_id", "order_item_id", "customer_id", "product_card_id",
    "order_date_dateorders", "shipping_date_dateorders",
    "sales", "net_revenue", "order_profit_per_order", "order_item_quantity",
    "order_item_discount", "order_item_discount_rate",
    "order_item_product_price", "order_item_profit_ratio",
    "order_item_total", "benefit_per_order", "sales_per_customer",
    "days_for_shipping_real", "days_for_shipment_scheduled",
    "shipping_delay_days", "shipping_performance",
    "late_delivery_risk", "is_fraud", "profit_category", "profit_tier",
    "discount_tier", "order_year", "order_month",
    "order_month_name", "order_quarter", "order_day_of_week", "order_week_number"
]
fact_cols_exist = [c for c in fact_cols if c in df.columns]
df_fact = clean_df(df[fact_cols_exist].copy())

cust_cols = [
    "customer_id", "customer_city", "customer_country",
    "customer_segment", "customer_state", "market",
    "latitude", "longitude"
]
cust_cols_exist = [c for c in cust_cols if c in df.columns]
df_dim_customer = df[cust_cols_exist].drop_duplicates(subset=["customer_id"]).reset_index(drop=True).copy()
df_dim_customer["customer_full_location"] = (
    df_dim_customer.get("customer_city", pd.Series(["Unknown"] * len(df_dim_customer))).astype(str)
    + ", " +
    df_dim_customer.get("customer_country", pd.Series(["Unknown"] * len(df_dim_customer))).astype(str)
)
df_dim_customer = clean_df(df_dim_customer)

prod_cols = [
    "product_card_id", "product_name", "product_price",
    "product_status", "category_id", "category_name",
    "department_id", "department_name", "product_category_id"
]
prod_cols_exist = [c for c in prod_cols if c in df.columns]
df_dim_product = df[prod_cols_exist].drop_duplicates(subset=["product_card_id"]).reset_index(drop=True).copy()
df_dim_product["stock_status"] = df_dim_product["product_status"].apply(
    lambda x: "In Stock" if x == 0 else "Out of Stock"
) if "product_status" in df_dim_product.columns else "Unknown"
df_dim_product["price_range"] = df_dim_product["product_price"].apply(
    lambda p: "Budget (<$50)" if p < 50 else (
        "Mid ($50-$200)" if p < 200 else (
            "Premium ($200-$500)" if p < 500 else "Luxury (>$500)"
        )
    )
) if "product_price" in df_dim_product.columns else "Unknown"
df_dim_product = clean_df(df_dim_product)

order_cols = [
    "order_id", "order_status", "order_region", "order_country",
    "order_city", "order_state", "shipping_mode", "delivery_status",
    "type", "order_customer_id"
]
order_cols_exist = [c for c in order_cols if c in df.columns]
df_dim_order = df[order_cols_exist].drop_duplicates(subset=["order_id"]).reset_index(drop=True).copy()
df_dim_order["status_group"] = df_dim_order["order_status"].apply(
    lambda s: "Completed" if "COMPLETE" in str(s).upper() else (
        "Cancelled" if "CANCEL" in str(s).upper() else (
            "Fraud" if "FRAUD" in str(s).upper() else (
                "Pending" if "PENDING" in str(s).upper() else "Other"
            )
        )
    )
) if "order_status" in df_dim_order.columns else "Other"
df_dim_order["delivery_risk_flag"] = df_dim_order["delivery_status"].apply(
    lambda s: "At Risk" if "Late" in str(s) else "Normal"
) if "delivery_status" in df_dim_order.columns else "Normal"
df_dim_order = clean_df(df_dim_order)

all_dates     = pd.date_range(start="2015-01-01", end="2018-12-31", freq="D")
df_dim_date   = pd.DataFrame({"Date": all_dates})
df_dim_date["Year"]           = df_dim_date["Date"].dt.year.astype(int)
df_dim_date["Month_Num"]      = df_dim_date["Date"].dt.month.astype(int)
df_dim_date["Month_Name"]     = df_dim_date["Date"].dt.strftime("%B")
df_dim_date["Quarter"]        = "Q" + df_dim_date["Date"].dt.quarter.astype(str)
df_dim_date["Day_of_Week"]    = df_dim_date["Date"].dt.day_name()
df_dim_date["Week_Number"]    = df_dim_date["Date"].dt.isocalendar().week.astype(int)
df_dim_date["Is_Weekend"]     = df_dim_date["Day_of_Week"].isin(["Saturday", "Sunday"])
df_dim_date["Year_Month"]     = df_dim_date["Date"].dt.strftime("%Y-%m")
df_dim_date["Fiscal_Quarter"] = "FY" + df_dim_date["Year"].astype(str) + "-" + df_dim_date["Quarter"]

print(f"     Fact_Orders:   {df_fact.shape[0]:,} rows")
print(f"     Dim_Customer:  {df_dim_customer.shape[0]:,} rows")
print(f"     Dim_Product:   {df_dim_product.shape[0]:,} rows")
print(f"     Dim_Order:     {df_dim_order.shape[0]:,} rows")
print(f"     Dim_Date:      {df_dim_date.shape[0]:,} rows")

print("\n--- Null Check Before Export ---")
for name, frame in [
    ("Fact_Orders",   df_fact),
    ("Dim_Customer",  df_dim_customer),
    ("Dim_Product",   df_dim_product),
    ("Dim_Order",     df_dim_order),
    ("Dim_Date",      df_dim_date),
]:
    nulls = frame.isnull().sum().sum()
    print(f"     {name:<20} nulls: {nulls}")
if not df_logs.empty:
    print(f"     {'Web_Access_Logs':<20} nulls: {df_logs.isnull().sum().sum()}")

print(f"\n[6/7] Writing Excel file: {OUTPUT_FILE}")

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    df_fact.to_excel(writer,         sheet_name="Fact_Orders",      index=False)
    df_dim_customer.to_excel(writer, sheet_name="Dim_Customer",     index=False)
    df_dim_product.to_excel(writer,  sheet_name="Dim_Product",      index=False)
    df_dim_order.to_excel(writer,    sheet_name="Dim_Order",        index=False)
    df_dim_date.to_excel(writer,     sheet_name="Dim_Date",         index=False)
    if not df_logs.empty:
        df_logs.head(100000).to_excel(writer, sheet_name="Web_Access_Logs", index=False)
    if not df_data_dict.empty:
        df_data_dict.to_excel(writer, sheet_name="Data_Dictionary", index=False)

print("     File saved successfully!")

print("\n[7/7] Final Summary:")
print("=" * 60)
print(f"  Original file:      {df_supply.shape[0]:,} rows x {df_supply.shape[1]} columns")
print(f"  After cleaning:     {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"  Fact_Orders:        {df_fact.shape[0]:,} rows x {df_fact.shape[1]} columns")
print(f"  Dim_Customer:       {df_dim_customer.shape[0]:,} unique customers")
print(f"  Dim_Product:        {df_dim_product.shape[0]:,} unique products")
print(f"  Dim_Order:          {df_dim_order.shape[0]:,} unique orders")
print(f"  Dim_Date:           {df_dim_date.shape[0]:,} days")
if not df_logs.empty:
    print(f"  Web_Access_Logs:    {min(len(df_logs), 100000):,} rows")
if not df_data_dict.empty:
    print(f"  Data_Dictionary:    {len(df_data_dict)} fields documented")
print(f"\n  Output: {OUTPUT_FILE}")
print("=" * 60)
print("\nDone!")
