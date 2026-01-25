# Tableau Integration Guide

## Dataset Schema (ecom_tableau_export.csv)

| Column | Type | Description |
|--------|------|-------------|
| order_id | INT | Unique order identifier |
| order_date | DATE | Date of the order (YYYY-MM-DD) |
| order_month | STRING | Month key for grouping (YYYY-MM) |
| quantity | INT | Number of units ordered |
| total_price | FLOAT | Total order value |
| status | STRING | completed / pending / refunded |
| user_id | INT | Customer ID |
| user_name | STRING | Customer full name |
| email | STRING | Customer email |
| city | STRING | Customer city |
| country | STRING | Customer country |
| segment | STRING | VIP / Regular / New |
| product_id | INT | Product ID |
| product_name | STRING | Product name |
| category | STRING | Product category |
| unit_price | FLOAT | Individual product price |

## Recommended Tableau Dashboards

### 1. Sales Trend Dashboard
- **Chart**: Line/Area chart
- **Columns**: ORDER_DATE (continuous, Month granularity)
- **Rows**: SUM(total_price)
- **Color**: status (filter to "completed")
- **Title**: Monthly Revenue Trend

### 2. Top Products Dashboard
- **Chart**: Horizontal Bar
- **Rows**: product_name
- **Columns**: SUM(total_price), sorted descending
- **Color**: category
- **Title**: Top Products by Revenue

### 3. Revenue Distribution
- **Chart**: Pie or Treemap
- **Dimension**: category
- **Measure**: SUM(total_price)
- **Label**: PERCENT_OF_TOTAL
- **Title**: Revenue by Category

### 4. Customer Geography Map
- **Chart**: Filled Map
- **Geographic**: country (auto-geocoded)
- **Color/Size**: SUM(total_price)
- **Title**: Revenue by Country

### 5. Customer Segments Analysis
- **Chart**: Bar + KPI tiles
- **Dimension**: segment
- **Measures**: COUNT(user_id), SUM(total_price), AVG(total_price)
- **Title**: Customer Segment Performance
change 7
change 11
change 16
change 34
