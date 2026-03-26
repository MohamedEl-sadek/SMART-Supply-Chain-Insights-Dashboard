# SMART Supply Chain Insights Dashboard

A complete end-to-end Supply Chain Analytics project built with Python, SQL Server, and Power BI. The project transforms raw supply chain data into a professional, interactive dashboard with 60+ DAX measures, a Star Schema database, and a full EDA report.

---

## Project Architecture

```
Raw Data (CSV)
     │
     ▼
┌─────────────────────────────┐
│   clean_and_merge.py        │  ← Python data pipeline
│   • Cleans 180,519 rows     │
│   • Builds Star Schema      │
│   • Exports Excel workbook  │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  SupplyChain_Cleaned_        │
│  Master.xlsx                │  ← 7 sheets: Fact + 4 Dims
│  • Fact_Orders (180K rows)  │     + Web Logs + Data Dict
│  • Dim_Customer (20K)       │
│  • Dim_Product (118)        │
│  • Dim_Order (65K)          │
│  • Dim_Date (1,461 days)    │
│  • Web_Access_Logs (100K)   │
│  • Data_Dictionary (73 flds)│
└──────┬──────────────────────┘
       │                  │
       ▼                  ▼
┌──────────────┐  ┌──────────────────────┐
│load_to_sql   │  │  EDA_SupplyChain_    │
│server.py     │  │  Report.py           │
│              │  │  • 10 analysis       │
│SQL Server DW │  │    sections          │
│(localdb)     │  │  • 19 charts saved   │
│SupplyChainDW │  │    as PNG            │
└──────┬───────┘  └──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Power BI Desktop           │
│  • 4 Dashboard Pages        │
│  • 60+ DAX Measures         │
│  • Star Schema Model        │
│  • Interactive Slicers      │
└─────────────────────────────┘
```

---

## Repository Structure

```
SMART-Supply-Chain-Insights/
│
├── data/
│   └── (place source CSV files here)
│       ├── DataCoSupplyChainDataset.csv
│       ├── tokenized_access_logs.csv
│       └── DescriptionDataCoSupplyChain.csv
│
├── python/
│   ├── clean_and_merge.py          ← Step 1: Data cleaning pipeline
│   ├── load_to_sqlserver.py        ← Step 2: Load to SQL Server
│   └── EDA_SupplyChain_Report.py   ← Step 3: Full EDA report
│
├── sql/
│   └── 04_Star_Schema_SQL.sql      ← Star Schema DDL + views
│
├── powerbi/
│   ├── 01_Power_Query_Transformations.md
│   ├── 02_DAX_Measures.md
│   ├── 02_Power_Query_for_PowerBI.txt
│   ├── 03_DAX_Measures_Complete.txt
│   └── 05_PowerBI_Step_by_Step_Guide.txt
│
└── README.md
```

---

## Data Pipeline — Step by Step

### Step 1 — Data Cleaning (`clean_and_merge.py`)

| Task | Detail |
|---|---|
| Input | 3 CSV files (Supply Chain + Access Logs + Data Dictionary) |
| Rows processed | 180,519 order lines |
| Encoding handled | Latin-1 fallback for special characters |
| Columns dropped | Email, Password, Street, Zipcode, Image, Description |
| Null handling | Mode imputation for dates, zero-fill for numeric, "Unknown" for text |
| Derived fields | 13 new columns: year, month, quarter, fraud flag, delay days, RFM bands, discount tiers |
| Output | `SupplyChain_Cleaned_Master.xlsx` — 7 sheets |

### Step 2 — SQL Server Load (`load_to_sqlserver.py`)

| Table | Rows | Description |
|---|---|---|
| Fact_Orders | 180,519 | Core transaction fact table |
| Dim_Customer | 20,652 | Unique customer profiles |
| Dim_Product | 118 | Product catalog |
| Dim_Order | 65,752 | Order-level attributes |
| Dim_Date | 1,461 | Date dimension (2015–2018) |
| Fact_WebLogs | 100,000 | Web access session logs |

**Connection:** `(localdb)\MSSQLLocalDB` · Database: `SupplyChainDW` · Driver: ODBC 18

### Step 3 — EDA Report (`EDA_SupplyChain_Report.py`)

10 analysis sections generating 19 charts:

| Section | Analysis |
|---|---|
| 1 | Dataset overview and row counts |
| 2 | Sales & revenue KPIs, monthly trend, year-over-year |
| 3 | Market performance, customer segments, RFM segmentation |
| 4 | Top products, department margins, discount impact |
| 5 | Shipping mode performance, late delivery rates |
| 6 | Fraud detection — by market and shipping mode |
| 7 | Geographic analysis — top 15 countries, sales vs margin |
| 8 | Web traffic — views, hourly patterns, add-to-cart rate |
| 9 | Correlation heatmap, distribution analysis |
| 10 | Auto-generated key findings summary table |

---

## Star Schema Design

```
                    ┌─────────────┐
                    │  Dim_Date   │
                    │  DateKey PK │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────┴──────┐  ┌──────┴──────┐  ┌─────┴───────┐
   │ Dim_Customer│  │ Fact_Orders │  │ Dim_Product │
   │ Customer_ID │◄─┤ Customer_ID │  │ Product_    │
   │ PK          │  │ Product_    ├─►│ Card_ID PK  │
   └─────────────┘  │ Card_ID     │  └─────────────┘
                    │ Order_ID    │
                    │ Order_DateK │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  Dim_Order  │
                    │  Order_ID PK│
                    └─────────────┘
```

---

## Power BI Dashboard — 4 Pages

### Page 1 — Executive Overview
- 5 KPI cards: Total Sales · Total Profit · Profit Margin % · Total Orders · Fraud Rate %
- Monthly sales and profit trend line
- Sales by market (horizontal bar)
- Orders by customer segment (donut)
- Slicers: Year · Market · Shipping Mode

### Page 2 — Sales & Revenue
- Top 5 products by sales
- Annual sales by year
- Profit by department
- Monthly sales trend
- Summary matrix by market and year

### Page 3 — Shipping Performance
- KPI cards: Late Delivery Rate % · Avg Delay · Late Count
- Late rate by shipping mode
- Orders by delivery status (donut)
- Late delivery rate by region (bar)
- Slicers: Year · Shipping Mode

### Page 4 — Fraud Detection
- KPI cards: Fraud Orders · Fraud Rate % · Fraud Revenue
- Fraud trend over time
- Fraud by region
- Fraud rate matrix by mode and market

---

## Key Findings

| Metric | Value |
|---|---|
| Total Sales | $36.78M |
| Total Profit | $3.97M |
| Profit Margin | 10.78% |
| Total Orders | 65,752 |
| Late Delivery Rate | 54.8% |
| Fraud Rate | ~2.2% |
| Top Market | Europe |
| Top Segment | Consumer (51.89%) |
| Analysis Period | Jan 2015 – Jan 2018 |

---

## DAX Measures (60+)

Key measure groups included:

- **Sales:** Total Sales, Total Profit, Profit Margin %, Avg Order Value, Discount Rate %
- **Time Intelligence:** Sales YTD, Sales MTD, Sales LY, YoY Growth %
- **Shipping:** Late Delivery Rate %, Avg Shipping Delay, Late Delivery Count
- **Fraud:** Fraud Orders, Fraud Rate %, Fraud Revenue
- **Customer:** RFM-based segmentation measures

Full measure definitions in `powerbi/03_DAX_Measures_Complete.txt`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Cleaning | Python 3.10 · pandas · numpy |
| EDA & Visualization | matplotlib · seaborn |
| Database | SQL Server LocalDB · ODBC Driver 18 |
| ETL to SQL | pyodbc · SQLAlchemy |
| BI Dashboard | Power BI Desktop |
| Output Format | Excel (.xlsx) · SQL (.sql) · PNG charts |

---

## How to Run

```bash
# 1. Install dependencies
pip install pandas numpy matplotlib seaborn openpyxl pyodbc sqlalchemy

# 2. Place source files in D:\SMART-Supply-Chain-Insights\
#    - DataCoSupplyChainDataset.csv
#    - tokenized_access_logs.csv
#    - DescriptionDataCoSupplyChain.csv

# 3. Run data cleaning pipeline
python clean_and_merge.py

# 4. Load to SQL Server
python load_to_sqlserver.py

# 5. Run EDA report (generates 19 PNG charts)
python EDA_SupplyChain_Report.py

# 6. Open Power BI Desktop and connect to:
#    Server: (localdb)\MSSQLLocalDB
#    Database: SupplyChainDW
```

---

## Author

**Mohamed El-Sadek**  
GitHub: [https://github.com/MohamedEl-sadek](https://github.com/MohamedEl-sadek)
