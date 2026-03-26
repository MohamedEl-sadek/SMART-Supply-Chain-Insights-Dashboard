import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

sns.set_theme(style='whitegrid', palette='deep')
plt.rcParams.update({
    'figure.dpi': 130,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.facecolor': 'white',
    'axes.facecolor': '#F8F9FA'
})

NAVY   = '#1E3A5F'
GREEN  = '#2ECC71'
RED    = '#E74C3C'
ORANGE = '#F39C12'
GREY   = '#95A5A6'

FILE    = r'D:\SMART-Supply-Chain-Insights\SupplyChain_Cleaned_Master.xlsx'
OUTDIR  = r'D:\SMART-Supply-Chain-Insights'

fact     = pd.read_excel(FILE, sheet_name='Fact_Orders')
customer = pd.read_excel(FILE, sheet_name='Dim_Customer')
product  = pd.read_excel(FILE, sheet_name='Dim_Product')
order    = pd.read_excel(FILE, sheet_name='Dim_Order')
date_df  = pd.read_excel(FILE, sheet_name='Dim_Date')
weblogs  = pd.read_excel(FILE, sheet_name='Web_Access_Logs')

fact.columns     = fact.columns.str.strip().str.lower()
customer.columns = customer.columns.str.strip().str.lower()
product.columns  = product.columns.str.strip().str.lower()
order.columns    = order.columns.str.strip().str.lower()
date_df.columns  = date_df.columns.str.strip().str.lower()
weblogs.columns  = weblogs.columns.str.strip().str.lower()

print("=" * 60)
print("SMART SUPPLY CHAIN INSIGHTS — EDA REPORT")
print("=" * 60)
print(f"Fact_Orders      : {fact.shape[0]:,} rows x {fact.shape[1]} cols")
print(f"Dim_Customer     : {customer.shape[0]:,} rows x {customer.shape[1]} cols")
print(f"Dim_Product      : {product.shape[0]:,} rows x {product.shape[1]} cols")
print(f"Dim_Order        : {order.shape[0]:,} rows x {order.shape[1]} cols")
print(f"Dim_Date         : {date_df.shape[0]:,} rows x {date_df.shape[1]} cols")
print(f"Web_Access_Logs  : {weblogs.shape[0]:,} rows x {weblogs.shape[1]} cols")


print("\n" + "=" * 60)
print("SECTION 1 — DATASET OVERVIEW")
print("=" * 60)
print(fact.describe(include='all').T.to_string())

tables = {
    'Fact_Orders': fact,
    'Dim_Customer': customer,
    'Dim_Product': product,
    'Dim_Order': order,
    'Web_Access_Logs': weblogs
}

fig, ax = plt.subplots(figsize=(10, 4))
names  = list(tables.keys())
counts = [len(v) for v in tables.values()]
bars   = ax.barh(names, counts, color=[NAVY, GREEN, ORANGE, RED, GREY])
for bar, c in zip(bars, counts):
    ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height() / 2,
            f'{c:,}', va='center', fontsize=10, fontweight='bold')
ax.set_xlabel('Row Count')
ax.set_title('Row Counts Across All Tables')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_01_RowCounts.png', bbox_inches='tight')
plt.show()


print("\n" + "=" * 60)
print("SECTION 2 — SALES & REVENUE ANALYSIS")
print("=" * 60)

merged = fact.merge(order, on='order_id', how='left') \
             .merge(customer, on='customer_id', how='left') \
             .merge(product, on='product_card_id', how='left')

fact['order_date_dateorders'] = pd.to_datetime(fact['order_date_dateorders'], errors='coerce')
date_df['date'] = pd.to_datetime(date_df['date'], errors='coerce')
merged['order_date_dateorders'] = pd.to_datetime(merged['order_date_dateorders'], errors='coerce')
merged['order_date_only'] = merged['order_date_dateorders'].dt.normalize()
merged = merged.merge(date_df, left_on='order_date_only', right_on='date', how='left')

total_sales   = merged['sales'].sum()
total_profit  = merged['order_profit_per_order'].sum()
total_orders  = merged['order_id'].nunique()
avg_order_val = total_sales / total_orders
profit_margin = (total_profit / total_sales) * 100

print(f"Total Sales      : ${total_sales:,.0f}")
print(f"Total Profit     : ${total_profit:,.0f}")
print(f"Total Orders     : {total_orders:,}")
print(f"Avg Order Value  : ${avg_order_val:,.2f}")
print(f"Profit Margin    : {profit_margin:.2f}%")

kpis = {
    'Total Sales ($M)':    round(total_sales / 1e6, 2),
    'Total Profit ($M)':   round(total_profit / 1e6, 2),
    'Total Orders (K)':    round(total_orders / 1e3, 1),
    'Avg Order Val ($)':   round(avg_order_val, 2),
    'Profit Margin (%)':   round(profit_margin, 2)
}

fig, axes = plt.subplots(1, 5, figsize=(16, 3))
colors = [NAVY, GREEN, ORANGE, GREY, RED]
for ax, (label, value), color in zip(axes, kpis.items(), colors):
    ax.set_facecolor(color)
    ax.text(0.5, 0.6, str(value), ha='center', va='center',
            fontsize=20, fontweight='bold', color='white', transform=ax.transAxes)
    ax.text(0.5, 0.2, label, ha='center', va='center',
            fontsize=9, color='white', transform=ax.transAxes)
    ax.axis('off')
plt.suptitle('Key Performance Indicators', fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_02_KPIs.png', bbox_inches='tight')
plt.show()

if 'year_month' in merged.columns:
    monthly = merged.groupby('year_month').agg(
        Sales=('sales', 'sum'),
        Profit=('order_profit_per_order', 'sum')
    ).reset_index().sort_values('year_month')

    fig, ax1 = plt.subplots(figsize=(14, 4))
    ax2 = ax1.twinx()
    ax1.fill_between(range(len(monthly)), monthly['Sales'], alpha=0.3, color=NAVY)
    ax1.plot(range(len(monthly)), monthly['Sales'], color=NAVY, linewidth=2, label='Total Sales')
    ax2.plot(range(len(monthly)), monthly['Profit'], color=GREEN, linewidth=2, linestyle='--', label='Total Profit')
    ax1.set_ylabel('Sales ($)', color=NAVY)
    ax2.set_ylabel('Profit ($)', color=GREEN)
    tick_step = max(1, len(monthly) // 12)
    ax1.set_xticks(range(0, len(monthly), tick_step))
    ax1.set_xticklabels(monthly['year_month'].iloc[::tick_step], rotation=45, ha='right')
    ax1.set_title('Monthly Sales and Profit Trend')
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    plt.tight_layout()
    plt.savefig(rf'{OUTDIR}\EDA_03_MonthlyTrend.png', bbox_inches='tight')
    plt.show()

if 'year' in merged.columns:
    yearly = merged.groupby('year').agg(
        Sales=('sales', 'sum'),
        Profit=('order_profit_per_order', 'sum')
    ).reset_index()
    yearly['Margin'] = (yearly['Profit'] / yearly['Sales']) * 100

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    axes[0].bar(yearly['year'].astype(str), yearly['Sales'] / 1e6, color=NAVY)
    axes[0].set_title('Annual Sales ($M)')
    axes[0].set_ylabel('Sales ($M)')
    for i, v in enumerate(yearly['Sales'] / 1e6):
        axes[0].text(i, v + 0.1, f'{v:.1f}M', ha='center', fontsize=9, fontweight='bold')

    axes[1].bar(yearly['year'].astype(str), yearly['Profit'] / 1e6, color=GREEN)
    axes[1].set_title('Annual Profit ($M)')
    axes[1].set_ylabel('Profit ($M)')
    for i, v in enumerate(yearly['Profit'] / 1e6):
        axes[1].text(i, v + 0.02, f'{v:.2f}M', ha='center', fontsize=9, fontweight='bold')

    axes[2].bar(yearly['year'].astype(str), yearly['Margin'], color=ORANGE)
    axes[2].set_title('Annual Profit Margin (%)')
    axes[2].set_ylabel('Margin (%)')
    for i, v in enumerate(yearly['Margin']):
        axes[2].text(i, v + 0.1, f'{v:.1f}%', ha='center', fontsize=9, fontweight='bold')

    plt.suptitle('Year-over-Year Performance', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(rf'{OUTDIR}\EDA_04_YearlyPerformance.png', bbox_inches='tight')
    plt.show()


print("\n" + "=" * 60)
print("SECTION 3 — CUSTOMER ANALYSIS")
print("=" * 60)

market_sales = merged.groupby('market').agg(
    Sales=('sales', 'sum'),
    Profit=('order_profit_per_order', 'sum'),
    Orders=('order_id', 'nunique')
).reset_index().sort_values('Sales', ascending=True)
market_sales['Margin'] = (market_sales['Profit'] / market_sales['Sales']) * 100
print(market_sales.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
bars = axes[0].barh(market_sales['market'], market_sales['Sales'] / 1e6, color=NAVY)
axes[0].set_title('Total Sales by Market ($M)')
axes[0].set_xlabel('Sales ($M)')
for bar, v in zip(bars, market_sales['Sales'] / 1e6):
    axes[0].text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                 f'{v:.1f}M', va='center', fontsize=9)

colors_m = [GREEN if m > 10 else RED for m in market_sales['Margin']]
bars2 = axes[1].barh(market_sales['market'], market_sales['Margin'], color=colors_m)
axes[1].set_title('Profit Margin % by Market')
axes[1].set_xlabel('Margin (%)')
axes[1].axvline(10, color=GREY, linestyle='--', linewidth=1, label='10% threshold')
for bar, v in zip(bars2, market_sales['Margin']):
    axes[1].text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                 f'{v:.1f}%', va='center', fontsize=9)
axes[1].legend()
plt.suptitle('Market Performance Overview', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_05_MarketPerformance.png', bbox_inches='tight')
plt.show()

seg = merged.groupby('customer_segment').agg(
    Sales=('sales', 'sum'),
    Orders=('order_id', 'nunique'),
    Customers=('customer_id', 'nunique')
).reset_index()
seg['Avg_Per_Customer'] = seg['Sales'] / seg['Customers']

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
axes[0].pie(seg['Sales'], labels=seg['customer_segment'],
            autopct='%1.1f%%', colors=[NAVY, GREEN, ORANGE], startangle=90, pctdistance=0.75)
axes[0].set_title('Sales Share by Segment')

axes[1].bar(seg['customer_segment'], seg['Orders'], color=[NAVY, GREEN, ORANGE])
axes[1].set_title('Total Orders by Segment')
axes[1].set_ylabel('Orders')

axes[2].bar(seg['customer_segment'], seg['Avg_Per_Customer'], color=[NAVY, GREEN, ORANGE])
axes[2].set_title('Avg Sales per Customer ($)')
axes[2].set_ylabel('Avg Sales ($)')

plt.suptitle('Customer Segment Analysis', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_06_CustomerSegments.png', bbox_inches='tight')
plt.show()

rfm_base = merged.copy()
rfm_base['order_date_dateorders'] = pd.to_datetime(rfm_base['order_date_dateorders'], errors='coerce')
snapshot = rfm_base['order_date_dateorders'].max()
rfm = rfm_base.groupby('customer_id').agg(
    Recency=('order_date_dateorders', lambda x: (snapshot - x.max()).days),
    Frequency=('order_id', 'nunique'),
    Monetary=('sales', 'sum')
).reset_index()

for col, label in [('Recency', 'R'), ('Frequency', 'F'), ('Monetary', 'M')]:
    _, bins = pd.qcut(rfm[col], 4, retbins=True, duplicates='drop')
    n_bins = len(bins) - 1
    if col == 'Recency':
        labels = list(range(n_bins, 0, -1))
    else:
        labels = list(range(1, n_bins + 1))
    rfm[label] = pd.cut(rfm[col], bins=bins, labels=labels, include_lowest=True)
rfm['RFM_Score'] = rfm['R'].astype(int) + rfm['F'].astype(int) + rfm['M'].astype(int)

def rfm_segment(score):
    if score >= 10: return 'Champions'
    elif score >= 8: return 'Loyal'
    elif score >= 6: return 'Potential'
    elif score >= 4: return 'At Risk'
    else: return 'Lost'

rfm['Segment'] = rfm['RFM_Score'].apply(rfm_segment)
seg_counts = rfm['Segment'].value_counts()
print("\nRFM Segment Distribution:")
print(seg_counts.to_string())

colors_rfm = [GREEN, NAVY, ORANGE, RED, GREY]
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].bar(seg_counts.index, seg_counts.values, color=colors_rfm)
axes[0].set_title('Customer Count by RFM Segment')
axes[0].set_ylabel('Number of Customers')
for i, v in enumerate(seg_counts.values):
    axes[0].text(i, v + 5, str(v), ha='center', fontsize=10, fontweight='bold')

seg_revenue = rfm.groupby('Segment')['Monetary'].sum().sort_values(ascending=False)
axes[1].bar(seg_revenue.index, seg_revenue.values / 1e6, color=colors_rfm)
axes[1].set_title('Revenue by RFM Segment ($M)')
axes[1].set_ylabel('Revenue ($M)')

plt.suptitle('RFM Customer Segmentation', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_07_RFM.png', bbox_inches='tight')
plt.show()


print("\n" + "=" * 60)
print("SECTION 4 — PRODUCT PERFORMANCE")
print("=" * 60)

top_products = merged.groupby('product_name').agg(
    Sales=('sales', 'sum'),
    Profit=('order_profit_per_order', 'sum'),
    Units=('order_item_quantity', 'sum')
).reset_index()
top_products['Margin'] = (top_products['Profit'] / top_products['Sales']) * 100

top10_sales  = top_products.nlargest(10, 'Sales')
top10_profit = top_products.nlargest(10, 'Profit')

print("\nTop 10 Products by Sales:")
print(top10_sales[['product_name', 'Sales', 'Profit', 'Margin']].to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
axes[0].barh(top10_sales['product_name'].str[:35], top10_sales['Sales'] / 1e6, color=NAVY)
axes[0].set_title('Top 10 Products by Sales ($M)')
axes[0].set_xlabel('Sales ($M)')
axes[0].invert_yaxis()

axes[1].barh(top10_profit['product_name'].str[:35], top10_profit['Profit'] / 1e3, color=GREEN)
axes[1].set_title('Top 10 Products by Profit ($K)')
axes[1].set_xlabel('Profit ($K)')
axes[1].invert_yaxis()

plt.suptitle('Product Performance Leaders', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_08_TopProducts.png', bbox_inches='tight')
plt.show()

dept = merged.groupby('department_name').agg(
    Sales=('sales', 'sum'),
    Profit=('order_profit_per_order', 'sum'),
    Units=('order_item_quantity', 'sum')
).reset_index().sort_values('Sales', ascending=False)
dept['Margin'] = (dept['Profit'] / dept['Sales']) * 100

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].bar(dept['department_name'], dept['Sales'] / 1e6, color=NAVY)
axes[0].set_title('Sales by Department ($M)')
axes[0].set_ylabel('Sales ($M)')
axes[0].tick_params(axis='x', rotation=45)

colors_dept = [GREEN if m > 0 else RED for m in dept['Margin']]
axes[1].bar(dept['department_name'], dept['Margin'], color=colors_dept)
axes[1].axhline(0, color='black', linewidth=0.8)
axes[1].set_title('Profit Margin % by Department')
axes[1].set_ylabel('Margin (%)')
axes[1].tick_params(axis='x', rotation=45)

plt.suptitle('Department-Level Analysis', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_09_Departments.png', bbox_inches='tight')
plt.show()

discount_bins   = [0, 0.05, 0.10, 0.15, 0.20, 0.25, 1.0]
discount_labels = ['0-5%', '5-10%', '10-15%', '15-20%', '20-25%', '25%+']
merged['discount_band'] = pd.cut(merged['order_item_discount_rate'],
                                  bins=discount_bins, labels=discount_labels)
disc = merged.groupby('discount_band').agg(
    Orders=('order_id', 'nunique'),
    Avg_Profit=('order_profit_per_order', 'mean')
).reset_index()

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
axes[0].bar(disc['discount_band'].astype(str), disc['Orders'], color=NAVY)
axes[0].set_title('Orders Count by Discount Band')
axes[0].set_ylabel('Orders')

bar_colors = [GREEN if v > 0 else RED for v in disc['Avg_Profit']]
axes[1].bar(disc['discount_band'].astype(str), disc['Avg_Profit'], color=bar_colors)
axes[1].axhline(0, color='black', linewidth=0.8)
axes[1].set_title('Avg Profit per Order by Discount Band')
axes[1].set_ylabel('Avg Profit ($)')

plt.suptitle('Discount Impact on Profitability', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_10_DiscountImpact.png', bbox_inches='tight')
plt.show()


print("\n" + "=" * 60)
print("SECTION 5 — SHIPPING & DELIVERY ANALYSIS")
print("=" * 60)

late_rate = merged['late_delivery_risk'].mean() * 100
avg_delay = merged['shipping_delay_days'].mean()
print(f"Overall Late Delivery Rate : {late_rate:.1f}%")
print(f"Average Shipping Delay     : {avg_delay:.1f} days")

by_mode = merged.groupby('shipping_mode').agg(
    Orders=('order_id', 'nunique'),
    Late_Rate=('late_delivery_risk', 'mean'),
    Avg_Delay=('shipping_delay_days', 'mean')
).reset_index()
by_mode['Late_Rate'] = by_mode['Late_Rate'] * 100
print("\nShipping Mode Performance:")
print(by_mode.to_string(index=False))

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
axes[0].bar(by_mode['shipping_mode'], by_mode['Orders'], color=NAVY)
axes[0].set_title('Orders by Shipping Mode')
axes[0].tick_params(axis='x', rotation=30)

bar_colors = [RED if r > 50 else ORANGE if r > 30 else GREEN for r in by_mode['Late_Rate']]
axes[1].bar(by_mode['shipping_mode'], by_mode['Late_Rate'], color=bar_colors)
axes[1].set_title('Late Delivery Rate % by Mode')
axes[1].set_ylabel('Late Rate (%)')
axes[1].tick_params(axis='x', rotation=30)
for i, v in enumerate(by_mode['Late_Rate']):
    axes[1].text(i, v + 0.5, f'{v:.1f}%', ha='center', fontsize=9)

axes[2].bar(by_mode['shipping_mode'], by_mode['Avg_Delay'], color=ORANGE)
axes[2].set_title('Avg Shipping Delay (Days) by Mode')
axes[2].set_ylabel('Avg Days')
axes[2].tick_params(axis='x', rotation=30)

plt.suptitle('Shipping Mode Performance', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_11_ShippingMode.png', bbox_inches='tight')
plt.show()

delivery_counts = merged['delivery_status'].value_counts()
region_late = merged.groupby('order_region').agg(
    Late_Rate=('late_delivery_risk', 'mean')
).reset_index().sort_values('Late_Rate', ascending=True)
region_late['Late_Rate'] = region_late['Late_Rate'] * 100

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].pie(delivery_counts.values, labels=delivery_counts.index,
            autopct='%1.1f%%', colors=[RED, ORANGE, GREEN, NAVY][:len(delivery_counts)],
            startangle=90)
axes[0].set_title('Orders by Delivery Status')

axes[1].barh(region_late['order_region'], region_late['Late_Rate'],
             color=[RED if r > 55 else ORANGE if r > 45 else GREEN for r in region_late['Late_Rate']])
axes[1].set_title('Late Delivery Rate % by Region')
axes[1].set_xlabel('Late Rate (%)')

plt.suptitle('Delivery Status & Regional Risk', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_12_DeliveryStatus.png', bbox_inches='tight')
plt.show()


print("\n" + "=" * 60)
print("SECTION 6 — FRAUD DETECTION ANALYSIS")
print("=" * 60)

print(f"Is_Fraud values:\n{merged['is_fraud'].value_counts().to_string()}")
fraud_mask = merged['is_fraud'].astype(str).str.lower() == 'fraud'
fraud_df   = merged[fraud_mask]
non_fraud  = merged[~fraud_mask]
fraud_rate = len(fraud_df) / len(merged) * 100
fraud_rev  = fraud_df['sales'].sum()
print(f"\nFraud Orders : {len(fraud_df):,} ({fraud_rate:.1f}%)")
print(f"Fraud Revenue: ${fraud_rev:,.0f}")

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
axes[0].pie([len(fraud_df), len(non_fraud)],
            labels=['Fraud', 'Legitimate'],
            autopct='%1.1f%%', colors=[RED, GREEN], startangle=90)
axes[0].set_title('Fraud vs Legitimate Orders')

fraud_market = merged.groupby('market').apply(
    lambda x: (fraud_mask[x.index].sum() / len(x)) * 100
).reset_index()
fraud_market.columns = ['market', 'Fraud_Rate']
fraud_market = fraud_market.sort_values('Fraud_Rate', ascending=True)
axes[1].barh(fraud_market['market'], fraud_market['Fraud_Rate'],
             color=[RED if v > 10 else ORANGE for v in fraud_market['Fraud_Rate']])
axes[1].set_title('Fraud Rate % by Market')
axes[1].set_xlabel('Fraud Rate (%)')

fraud_mode = merged.groupby('shipping_mode').apply(
    lambda x: (fraud_mask[x.index].sum() / len(x)) * 100
).reset_index()
fraud_mode.columns = ['shipping_mode', 'Fraud_Rate']
axes[2].bar(fraud_mode['shipping_mode'], fraud_mode['Fraud_Rate'], color=RED)
axes[2].set_title('Fraud Rate % by Shipping Mode')
axes[2].set_ylabel('Fraud Rate (%)')
axes[2].tick_params(axis='x', rotation=30)

plt.suptitle('Fraud Analysis', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_13_Fraud.png', bbox_inches='tight')
plt.show()


print("\n" + "=" * 60)
print("SECTION 7 — GEOGRAPHIC ANALYSIS")
print("=" * 60)

country_perf = merged.groupby(['market', 'order_country']).agg(
    Sales=('sales', 'sum'),
    Profit=('order_profit_per_order', 'sum'),
    Orders=('order_id', 'nunique')
).reset_index()
country_perf['Margin'] = (country_perf['Profit'] / country_perf['Sales']) * 100
top_countries = country_perf.nlargest(15, 'Sales')
print("\nTop 15 Countries by Sales:")
print(top_countries[['order_country', 'market', 'Sales', 'Profit', 'Margin']].to_string(index=False))

avg_margin = country_perf['Margin'].mean()

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
axes[0].barh(top_countries['order_country'], top_countries['Sales'] / 1e6, color=NAVY)
axes[0].set_title('Top 15 Countries by Sales ($M)')
axes[0].set_xlabel('Sales ($M)')
axes[0].invert_yaxis()

axes[1].scatter(top_countries['Sales'] / 1e6, top_countries['Margin'],
                s=top_countries['Orders'] / 5,
                c=[NAVY if m > avg_margin else RED for m in top_countries['Margin']],
                alpha=0.7)
for _, row in top_countries.iterrows():
    axes[1].annotate(row['order_country'], (row['Sales'] / 1e6, row['Margin']), fontsize=7, ha='left')
axes[1].set_title('Sales vs Margin by Country (bubble = orders)')
axes[1].set_xlabel('Sales ($M)')
axes[1].set_ylabel('Profit Margin (%)')
axes[1].axhline(avg_margin, color=GREY, linestyle='--', linewidth=1)

plt.suptitle('Geographic Performance', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_14_Geography.png', bbox_inches='tight')
plt.show()


print("\n" + "=" * 60)
print("SECTION 8 — WEB TRAFFIC & BEHAVIOR ANALYSIS")
print("=" * 60)

print(f"Total Web Sessions     : {len(weblogs):,}")
product_col  = 'product' if 'product' in weblogs.columns else 'product_name'
category_col = 'category' if 'category' in weblogs.columns else 'category_name'
hour_col     = 'hour' if 'hour' in weblogs.columns else None
cart_col     = 'is_add_to_cart' if 'is_add_to_cart' in weblogs.columns else None

print(f"Unique Products Viewed : {weblogs[product_col].nunique():,}")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

top_viewed = weblogs[product_col].value_counts().head(10)
axes[0, 0].barh(top_viewed.index[::-1], top_viewed.values[::-1], color=NAVY)
axes[0, 0].set_title('Top 10 Most Viewed Products')
axes[0, 0].set_xlabel('Page Views')

top_cats = weblogs[category_col].value_counts().head(10)
axes[0, 1].barh(top_cats.index[::-1], top_cats.values[::-1], color=GREEN)
axes[0, 1].set_title('Top 10 Most Viewed Categories')
axes[0, 1].set_xlabel('Page Views')

if hour_col:
    hourly = weblogs.groupby(hour_col).size().reset_index(name='Sessions')
    axes[1, 0].bar(hourly[hour_col], hourly['Sessions'], color=ORANGE)
    axes[1, 0].set_title('Web Traffic by Hour of Day')
    axes[1, 0].set_xlabel('Hour')
    axes[1, 0].set_ylabel('Sessions')

if cart_col:
    add_cart = weblogs[cart_col].value_counts()
    axes[1, 1].pie(add_cart.values, labels=['Not Added', 'Added to Cart'],
                   autopct='%1.1f%%', colors=[GREY, GREEN], startangle=90)
    axes[1, 1].set_title('Add-to-Cart Conversion Rate')

plt.suptitle('Web Access Log Insights', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_15_WebLogs.png', bbox_inches='tight')
plt.show()

web_views = weblogs[product_col].value_counts().reset_index()
web_views.columns = ['product_name', 'Views']
product_sales_agg = merged.groupby('product_name').agg(Sales=('sales', 'sum')).reset_index()
view_vs_sales = web_views.merge(product_sales_agg, on='product_name', how='inner').head(50)
corr = view_vs_sales[['Views', 'Sales']].corr().iloc[0, 1]
print(f"\nCorrelation (Views vs Sales): {corr:.2f}")

fig, ax = plt.subplots(figsize=(10, 5))
ax.scatter(view_vs_sales['Views'], view_vs_sales['Sales'] / 1e3, color=NAVY, alpha=0.6)
ax.set_title('Product Views vs Sales — Top 50 Products')
ax.set_xlabel('Web Views')
ax.set_ylabel('Sales ($K)')
ax.text(0.05, 0.93, f'Correlation: {corr:.2f}', transform=ax.transAxes, fontsize=11,
        bbox=dict(boxstyle='round', facecolor=GREEN, alpha=0.3))
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_16_ViewsVsSales.png', bbox_inches='tight')
plt.show()


print("\n" + "=" * 60)
print("SECTION 9 — CORRELATION & DISTRIBUTION ANALYSIS")
print("=" * 60)

numeric_cols = ['sales', 'order_profit_per_order', 'order_item_quantity',
                'order_item_discount_rate', 'late_delivery_risk', 'shipping_delay_days']
available = [c for c in numeric_cols if c in merged.columns]
corr_matrix = merged[available].corr()
print("\nCorrelation Matrix:")
print(corr_matrix.round(3).to_string())

fig, ax = plt.subplots(figsize=(9, 7))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn',
            mask=mask, ax=ax, linewidths=0.5, center=0, vmin=-1, vmax=1)
ax.set_title('Correlation Matrix — Key Numeric Fields', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_17_Correlation.png', bbox_inches='tight')
plt.show()

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
axes[0].hist(merged['sales'], bins=50, color=NAVY, edgecolor='white')
axes[0].set_title('Sales Distribution')
axes[0].set_xlabel('Sale Amount ($)')

axes[1].hist(merged['order_profit_per_order'], bins=50, color=GREEN, edgecolor='white')
axes[1].set_title('Profit Distribution')
axes[1].set_xlabel('Profit ($)')

axes[2].hist(merged['shipping_delay_days'].dropna(), bins=30, color=ORANGE, edgecolor='white')
axes[2].set_title('Shipping Delay Distribution')
axes[2].set_xlabel('Delay (Days)')

plt.suptitle('Distribution Analysis', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_18_Distributions.png', bbox_inches='tight')
plt.show()


print("\n" + "=" * 60)
print("SECTION 10 — KEY FINDINGS SUMMARY")
print("=" * 60)

top_market   = merged.groupby('market')['sales'].sum().idxmax()
top_dept     = merged.groupby('department_name')['order_profit_per_order'].sum().idxmax()
top_product  = merged.groupby('product_name')['sales'].sum().idxmax()
top_segment  = merged.groupby('customer_segment')['order_id'].nunique().idxmax()
worst_region = merged.groupby('order_region')['late_delivery_risk'].mean().idxmax()
best_mode    = merged.groupby('shipping_mode')['late_delivery_risk'].mean().idxmin()
worst_mode   = merged.groupby('shipping_mode')['late_delivery_risk'].mean().idxmax()

findings = [
    ('Top Market by Sales',            top_market),
    ('Top Department by Profit',       top_dept),
    ('Top Product by Sales',           top_product[:50]),
    ('Highest Order Segment',          top_segment),
    ('Highest Late Delivery Region',   worst_region),
    ('Best Shipping Mode (On-time)',   best_mode),
    ('Worst Shipping Mode (Late)',     worst_mode),
    ('Overall Profit Margin',          f'{round(profit_margin, 1)}%'),
    ('Overall Late Delivery Rate',     f'{round(late_rate, 1)}%'),
    ('Total Records Analyzed',         f'{len(merged):,}'),
]

print(f"\n{'Finding':<40} {'Value'}")
print("-" * 65)
for f, v in findings:
    print(f"{f:<40} {v}")

fig, ax = plt.subplots(figsize=(12, 5))
ax.axis('off')
tbl = ax.table(cellText=[[f, v] for f, v in findings],
               colLabels=['Finding', 'Value'],
               loc='center', cellLoc='left')
tbl.auto_set_font_size(False)
tbl.set_fontsize(10)
tbl.scale(1.2, 1.8)
for (row, col), cell in tbl.get_celld().items():
    if row == 0:
        cell.set_facecolor(NAVY)
        cell.set_text_props(color='white', fontweight='bold')
    elif row % 2 == 0:
        cell.set_facecolor('#EAF2FB')
    cell.set_edgecolor('#CCCCCC')
ax.set_title('EDA Key Findings Summary', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(rf'{OUTDIR}\EDA_19_KeyFindings.png', bbox_inches='tight')
plt.show()

print("\n" + "=" * 60)
print("EDA COMPLETE — All 19 charts saved to D:\\SMART-Supply-Chain-Insights\\")
print("=" * 60)
