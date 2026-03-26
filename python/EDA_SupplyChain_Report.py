egion_late['Late_Rate']])
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
