import sqlite3
import pandas as pd
import csv

# ======================================
# 1. Connect to database
# ======================================
conn = sqlite3.connect("xyz_sales.db")   # change this to your database file
cur = conn.cursor()

# ======================================
# 2. SQL solution
# ======================================
sql_query = """
SELECT c.CustomerID, c.Age, i.ItemName, SUM(od.Quantity) AS TotalQuantity
FROM Customers c
JOIN Orders o ON c.CustomerID = o.CustomerID
JOIN OrderDetails od ON o.OrderID = od.OrderID
JOIN Items i ON od.ItemID = i.ItemID
WHERE c.Age BETWEEN 18 AND 35
  AND od.Quantity IS NOT NULL
GROUP BY c.CustomerID, c.Age, i.ItemName
HAVING SUM(od.Quantity) > 0;
"""

sql_result = cur.execute(sql_query).fetchall()

# Save SQL results to CSV
with open("output_sql.csv", "w", newline="") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["CustomerID", "Age", "ItemName", "TotalQuantity"])
    writer.writerows(sql_result)

print("SQL results saved to output_sql.csv")

# ======================================
# 3. Pandas solution
# ======================================
# Load each table into pandas
customers = pd.read_sql("SELECT * FROM Customers", conn)
orders = pd.read_sql("SELECT * FROM Orders", conn)
order_details = pd.read_sql("SELECT * FROM OrderDetails", conn)
items = pd.read_sql("SELECT * FROM Items", conn)

# Merge step by step
cust_orders = customers.merge(orders, on="CustomerID")
cust_orders_details = cust_orders.merge(order_details, on="OrderID")
merged = cust_orders_details.merge(items, on="ItemID")

# Filter age 18–35
merged = merged[(merged["Age"] >= 18) & (merged["Age"] <= 35)]

# Replace missing quantities with 0
merged["Quantity"] = merged["Quantity"].fillna(0).astype(int)

# Group by Customer, Age, Item and sum Quantity
final_data = merged.groupby(["CustomerID", "Age", "ItemName"], as_index=False)["Quantity"].sum()

# Remove rows where Quantity = 0
final_data = final_data[final_data["Quantity"] > 0]

# Save Pandas results to CSV
final_data.to_csv("output_pandas.csv", sep=";", index=False)



conn.close()

