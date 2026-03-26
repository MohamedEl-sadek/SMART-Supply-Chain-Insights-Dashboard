# DAX Measures — SMART Supply Chain Dashboard
# افتح Power BI Desktop → New Measure → انسخ كل measure

## =============================================
## المجموعة 1: مقاييس المبيعات (Sales KPIs)
## =============================================

### إجمالي المبيعات
```dax
Total Sales = SUM(FactOrders[Sales])
```

### إجمالي الأرباح
```dax
Total Profit = SUM(FactOrders[Order Profit Per Order])
```

### هامش الربح %
```dax
Profit Margin % = 
DIVIDE(
    [Total Profit],
    [Total Sales],
    0
) * 100
```

### متوسط المبيعات لكل طلب
```dax
Avg Sales Per Order = 
DIVIDE(
    [Total Sales],
    [Total Orders],
    0
)
```

### إجمالي الخصم
```dax
Total Discount = SUM(FactOrders[Order Item Discount])
```

### نسبة الخصم
```dax
Discount Rate % = 
DIVIDE(
    [Total Discount],
    [Total Sales] + [Total Discount],
    0
) * 100
```

### المبيعات للفترة السابقة (Year over Year)
```dax
Sales PY = 
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR(DimDate[Date])
)
```

### نمو المبيعات YoY %
```dax
Sales YoY Growth % = 
DIVIDE(
    [Total Sales] - [Sales PY],
    [Sales PY],
    0
) * 100
```

### مبيعات الشهر الحالي MTD
```dax
Sales MTD = 
CALCULATE(
    [Total Sales],
    DATESMTD(DimDate[Date])
)
```

### مبيعات السنة الحالية YTD
```dax
Sales YTD = 
CALCULATE(
    [Total Sales],
    DATESYTD(DimDate[Date])
)
```

---

## =============================================
## المجموعة 2: مقاييس الطلبات (Orders KPIs)
## =============================================

### إجمالي عدد الطلبات
```dax
Total Orders = 
DISTINCTCOUNT(FactOrders[Order Id])
```

### إجمالي عدد العناصر المطلوبة
```dax
Total Items Ordered = SUM(FactOrders[Order Item Quantity])
```

### الطلبات المكتملة
```dax
Completed Orders = 
CALCULATE(
    [Total Orders],
    FactOrders[Order Status] = "COMPLETE"
)
```

### الطلبات الملغاة
```dax
Cancelled Orders = 
CALCULATE(
    [Total Orders],
    FactOrders[Order Status] = "CANCELED"
)
```

### الطلبات المشبوهة (احتيال)
```dax
Suspected Fraud Orders = 
CALCULATE(
    [Total Orders],
    FactOrders[Order Status] = "SUSPECTED_FRAUD"
)
```

### معدل إتمام الطلبات %
```dax
Order Completion Rate % = 
DIVIDE(
    [Completed Orders],
    [Total Orders],
    0
) * 100
```

### معدل إلغاء الطلبات %
```dax
Cancellation Rate % = 
DIVIDE(
    [Cancelled Orders],
    [Total Orders],
    0
) * 100
```

### معدل الاحتيال %
```dax
Fraud Rate % = 
DIVIDE(
    [Suspected Fraud Orders],
    [Total Orders],
    0
) * 100
```

### الطلبات قيد المعالجة
```dax
Pending Orders = 
CALCULATE(
    [Total Orders],
    FactOrders[Order Status] IN {"PENDING", "PENDING_PAYMENT", "PROCESSING", "ON_HOLD", "PAYMENT_REVIEW"}
)
```

---

## =============================================
## المجموعة 3: مقاييس الشحن والتوصيل (Shipping KPIs)
## =============================================

### متوسط أيام الشحن الفعلية
```dax
Avg Shipping Days (Actual) = 
AVERAGE(FactOrders[Days for shipping (real)])
```

### متوسط أيام الشحن المجدولة
```dax
Avg Shipping Days (Scheduled) = 
AVERAGE(FactOrders[Days for shipment (scheduled)])
```

### الطلبات المتأخرة
```dax
Late Deliveries = 
CALCULATE(
    [Total Orders],
    FactOrders[Delivery Status] = "Late delivery"
)
```

### الطلبات في الوقت المحدد
```dax
On Time Deliveries = 
CALCULATE(
    [Total Orders],
    FactOrders[Delivery Status] = "Shipping on time"
)
```

### الطلبات الملغاة للشحن
```dax
Cancelled Shipments = 
CALCULATE(
    [Total Orders],
    FactOrders[Delivery Status] = "Shipping canceled"
)
```

### معدل التأخر %
```dax
Late Delivery Rate % = 
DIVIDE(
    [Late Deliveries],
    [Total Orders],
    0
) * 100
```

### معدل التوصيل في الوقت %
```dax
On Time Delivery Rate % = 
DIVIDE(
    [On Time Deliveries],
    [Total Orders],
    0
) * 100
```

### متوسط فارق الشحن (تأخر أو تقدم)
```dax
Avg Shipping Gap Days = 
AVERAGE(FactOrders[Days for shipping (real)]) - AVERAGE(FactOrders[Days for shipment (scheduled)])
```

---

## =============================================
## المجموعة 4: مقاييس العملاء (Customer KPIs)
## =============================================

### إجمالي عدد العملاء
```dax
Total Customers = 
DISTINCTCOUNT(FactOrders[Customer Id])
```

### متوسط المبيعات لكل عميل
```dax
Avg Sales Per Customer = 
DIVIDE(
    [Total Sales],
    [Total Customers],
    0
)
```

### عملاء المستهلكين (Consumer)
```dax
Consumer Customers = 
CALCULATE(
    [Total Customers],
    FactOrders[Customer Segment] = "Consumer"
)
```

### عملاء الشركات (Corporate)
```dax
Corporate Customers = 
CALCULATE(
    [Total Customers],
    FactOrders[Customer Segment] = "Corporate"
)
```

### عملاء المكتب المنزلي
```dax
Home Office Customers = 
CALCULATE(
    [Total Customers],
    FactOrders[Customer Segment] = "Home Office"
)
```

### أفضل 10 عملاء بالمبيعات
```dax
Top 10 Customers Sales = 
CALCULATE(
    [Total Sales],
    TOPN(10, VALUES(FactOrders[Customer Id]), [Total Sales], DESC)
)
```

---

## =============================================
## المجموعة 5: مقاييس المنتجات (Product KPIs)
## =============================================

### إجمالي عدد المنتجات
```dax
Total Products = 
DISTINCTCOUNT(FactOrders[Product Card Id])
```

### أعلى منتج مبيعاً
```dax
Top Product by Sales = 
CALCULATE(
    FIRSTNONBLANK(FactOrders[Product Name], 1),
    TOPN(1, VALUES(FactOrders[Product Name]), [Total Sales], DESC)
)
```

### متوسط سعر المنتج
```dax
Avg Product Price = 
AVERAGE(FactOrders[Product Price])
```

### متوسط نسبة الربح للمنتج
```dax
Avg Profit Ratio = 
AVERAGE(FactOrders[Order Item Profit Ratio])
```

---

## =============================================
## المجموعة 6: مقاييس الجغرافيا (Geographic KPIs)
## =============================================

### المبيعات حسب السوق
```dax
Sales by Market = 
CALCULATE(
    [Total Sales],
    ALLEXCEPT(FactOrders, FactOrders[Market])
)
```

### مبيعات السوق الأفريقي
```dax
Africa Sales = 
CALCULATE([Total Sales], FactOrders[Market] = "Africa")
```

### مبيعات أوروبا
```dax
Europe Sales = 
CALCULATE([Total Sales], FactOrders[Market] = "Europe")
```

### مبيعات آسيا والمحيط الهادئ
```dax
Pacific Asia Sales = 
CALCULATE([Total Sales], FactOrders[Market] = "Pacific Asia")
```

### مبيعات أمريكا اللاتينية
```dax
LATAM Sales = 
CALCULATE([Total Sales], FactOrders[Market] = "LATAM")
```

### مبيعات أمريكا الشمالية
```dax
USCA Sales = 
CALCULATE([Total Sales], FactOrders[Market] = "USCA")
```

---

## =============================================
## المجموعة 7: مقاييس الاحتيال (Fraud KPIs)
## =============================================

### إجمالي خسائر الاحتيال
```dax
Total Fraud Loss = 
CALCULATE(
    [Total Sales],
    FactOrders[Order Status] = "SUSPECTED_FRAUD"
)
```

### متوسط قيمة طلب الاحتيال
```dax
Avg Fraud Order Value = 
CALCULATE(
    AVERAGE(FactOrders[Sales]),
    FactOrders[Order Status] = "SUSPECTED_FRAUD"
)
```

### أعلى منطقة احتيالاً
```dax
Top Fraud Region = 
CALCULATE(
    FIRSTNONBLANK(FactOrders[Order Region], 1),
    TOPN(1, VALUES(FactOrders[Order Region]), [Suspected Fraud Orders], DESC)
)
```

### الاحتيال مع تأخر الشحن
```dax
Fraud with Late Delivery = 
CALCULATE(
    [Suspected Fraud Orders],
    FactOrders[Late_delivery_risk] = 1
)
```

---

## =============================================
## مقاييس الـ KPI Cards (للعرض في بطاقات الأرقام)
## =============================================

### ملخص الأداء الكلي
```dax
Overall Performance Score = 
VAR CompletionScore = [Order Completion Rate %] * 0.4
VAR OnTimeScore = [On Time Delivery Rate %] * 0.4
VAR FraudPenalty = [Fraud Rate %] * 0.2
RETURN
    CompletionScore + OnTimeScore - FraudPenalty
```

### نص حالة الأداء
```dax
Performance Status = 
VAR Score = [Overall Performance Score]
RETURN
    IF(Score >= 80, "Excellent ✅",
    IF(Score >= 60, "Good 🟡",
    IF(Score >= 40, "Average ⚠️", "Poor ❌")))
```
