# Power Query (M Language) — SMART Supply Chain Dashboard
# انسخ هذه الكود في Power Query Editor في Power BI

## الخطوة 1: تحميل البيانات من GitHub أو من جهازك

### تحميل الملف المنظف (DataCo_cleaned.xls)
```m
let
    Source = Excel.Workbook(
        File.Contents("C:\SupplyChain\DataCo_cleaned.xls"), 
        null, true
    ),
    Sheet1 = Source{[Item="Sheet1",Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Sheet1, [PromoteAllScalars=true]),
    
    // تحويل أنواع البيانات
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {
        {"Type", type text},
        {"Days for shipping (real)", Int64.Type},
        {"Days for shipment (scheduled)", Int64.Type},
        {"Benefit per order", type number},
        {"Sales per customer", type number},
        {"Delivery Status", type text},
        {"Late_delivery_risk", Int64.Type},
        {"Category Id", Int64.Type},
        {"Category Name", type text},
        {"Customer City", type text},
        {"Customer Country", type text},
        {"Customer Id", Int64.Type},
        {"Customer Segment", type text},
        {"Department Id", Int64.Type},
        {"Department Name", type text},
        {"Latitude", type number},
        {"Longitude", type number},
        {"Market", type text},
        {"Order City", type text},
        {"Order Country", type text},
        {"Order Customer Id", Int64.Type},
        {"order date (DateOrders)", type datetime},
        {"Order Id", Int64.Type},
        {"Order Item Discount", type number},
        {"Order Item Discount Rate", type number},
        {"Order Item Id", Int64.Type},
        {"Order Item Product Price", type number},
        {"Order Item Profit Ratio", type number},
        {"Order Item Quantity", Int64.Type},
        {"Sales", type number},
        {"Order Item Total", type number},
        {"Order Profit Per Order", type number},
        {"Order Region", type text},
        {"Order State", type text},
        {"Order Status", type text},
        {"Product Card Id", Int64.Type},
        {"Product Category Id", Int64.Type},
        {"Product Name", type text},
        {"Product Price", type number},
        {"Product Status", Int64.Type},
        {"Shipping date (DateOrders)", type datetime},
        {"Shipping Mode", type text}
    }),
    
    // إزالة الأعمدة غير الضرورية
    RemovedColumns = Table.RemoveColumns(ChangedTypes, {
        "Customer Email", "Customer Password", "Product Description", 
        "Product Image", "Customer Street", "Customer Zipcode"
    }),
    
    // إضافة عمود الشهر
    AddedOrderMonth = Table.AddColumn(RemovedColumns, "Order Month", 
        each Date.Month([order date (DateOrders)]), Int64.Type),
    
    // إضافة عمود السنة
    AddedOrderYear = Table.AddColumn(AddedOrderMonth, "Order Year", 
        each Date.Year([order date (DateOrders)]), Int64.Type),
    
    // إضافة اسم الشهر
    AddedMonthName = Table.AddColumn(AddedOrderYear, "Month Name", 
        each Date.MonthName([order date (DateOrders)]), type text),
    
    // إضافة عمود ربع السنة
    AddedQuarter = Table.AddColumn(AddedMonthName, "Quarter", 
        each "Q" & Text.From(Date.QuarterOfYear([order date (DateOrders)])), type text),
    
    // إضافة عمود تأخر الشحن (بالأيام)
    AddedShippingDelay = Table.AddColumn(AddedQuarter, "Shipping Delay Days", 
        each [Days for shipping (real)] - [Days for shipment (scheduled)], Int64.Type),
    
    // إضافة عمود حالة الاحتيال
    AddedFraudFlag = Table.AddColumn(AddedShippingDelay, "Is Fraud", 
        each if [Order Status] = "SUSPECTED_FRAUD" then "Fraud" else "Legitimate", type text),
    
    // إضافة ربحية المنتج
    AddedProfitCategory = Table.AddColumn(AddedFraudFlag, "Profit Category", 
        each if [Order Item Profit Ratio] > 0.2 then "High Profit"
             else if [Order Item Profit Ratio] > 0 then "Low Profit"
             else "Loss", type text),
    
    // إضافة تصنيف وقت الشحن
    AddedShippingClass = Table.AddColumn(AddedProfitCategory, "Shipping Performance", 
        each if [Days for shipping (real)] < [Days for shipment (scheduled)] then "Early"
             else if [Days for shipping (real)] = [Days for shipment (scheduled)] then "On Time"
             else "Late", type text)

in
    AddedShippingClass
```

---

## الخطوة 2: إنشاء جدول التاريخ (Date Table)
```m
let
    StartDate = #date(2015, 1, 1),
    EndDate = #date(2018, 12, 31),
    NumberOfDays = Duration.Days(EndDate - StartDate) + 1,
    
    DateList = List.Dates(StartDate, NumberOfDays, #duration(1, 0, 0, 0)),
    DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    
    ChangedType = Table.TransformColumnTypes(DateTable, {{"Date", type date}}),
    
    AddedYear = Table.AddColumn(ChangedType, "Year", each Date.Year([Date]), Int64.Type),
    AddedMonth = Table.AddColumn(AddedYear, "Month Number", each Date.Month([Date]), Int64.Type),
    AddedMonthName = Table.AddColumn(AddedMonth, "Month Name", each Date.MonthName([Date]), type text),
    AddedQuarter = Table.AddColumn(AddedMonthName, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    AddedDayOfWeek = Table.AddColumn(AddedQuarter, "Day of Week", each Date.DayOfWeekName([Date]), type text),
    AddedWeekNum = Table.AddColumn(AddedDayOfWeek, "Week Number", each Date.WeekOfYear([Date]), Int64.Type),
    AddedYearMonth = Table.AddColumn(AddedWeekNum, "Year-Month", each Text.From([Year]) & "-" & Text.PadStart(Text.From([Month Number]), 2, "0"), type text),
    AddedIsWeekend = Table.AddColumn(AddedYearMonth, "Is Weekend", 
        each if Date.DayOfWeek([Date]) >= 5 then "Weekend" else "Weekday", type text)

in
    AddedIsWeekend
```

---

## الخطوة 3: إنشاء جدول العملاء (Dim_Customer)
```m
let
    Source = FactOrders,
    SelectColumns = Table.SelectColumns(Source, {
        "Customer Id", "Customer City", "Customer Country",
        "Customer Segment", "Customer State"
    }),
    RemovedDuplicates = Table.Distinct(SelectColumns),
    SortedRows = Table.Sort(RemovedDuplicates, {{"Customer Id", Order.Ascending}})
in
    SortedRows
```

---

## الخطوة 4: إنشاء جدول المنتجات (Dim_Product)
```m
let
    Source = FactOrders,
    SelectColumns = Table.SelectColumns(Source, {
        "Product Card Id", "Product Name", "Product Price",
        "Product Status", "Category Id", "Category Name",
        "Department Id", "Department Name", "Product Category Id"
    }),
    RemovedDuplicates = Table.Distinct(SelectColumns),
    AddedAvailability = Table.AddColumn(RemovedDuplicates, "Is Available",
        each if [Product Status] = 0 then "Available" else "Out of Stock", type text)
in
    AddedAvailability
```

---

## الخطوة 5: إنشاء جدول الشحن (Dim_Shipping)
```m
let
    Source = FactOrders,
    SelectColumns = Table.SelectColumns(Source, {
        "Order Id", "Shipping Mode", "Delivery Status",
        "Late_delivery_risk", "Days for shipping (real)",
        "Days for shipment (scheduled)", "Shipping date (DateOrders)"
    }),
    RemovedDuplicates = Table.Distinct(SelectColumns)
in
    RemovedDuplicates
```
