import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

# ---- DB Connection ----
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ---- Load CSV ----
print("📂 Reading CSV...")
df = pd.read_csv("data/sales_data_sample.csv", encoding="latin1")

# ---- Clean Column Names (lowercase) ----
df.columns = df.columns.str.lower().str.strip()
print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
print(df.head(3))

# ---- Split into Separate Tables ----

# 1. Customers Table
customers = df[[
    "customername", "phone", "addressline1",
    "city", "state", "postalcode", "country",
    "contactlastname", "contactfirstname"
]].drop_duplicates(subset=["customername"]).reset_index(drop=True)

customers.insert(0, "customer_id", range(1, len(customers) + 1))
customers.columns = [
    "customer_id", "customer_name", "phone", "address",
    "city", "state", "postal_code", "country",
    "contact_lastname", "contact_firstname"
]

# 2. Products Table
products = df[[
    "productcode", "productline", "msrp"
]].drop_duplicates(subset=["productcode"]).reset_index(drop=True)

products.insert(0, "product_id", range(1, len(products) + 1))
products.columns = ["product_id", "product_code", "product_line", "msrp"]

# 3. Orders Table
# Merge to get customer_id and product_id
orders = df[[
    "ordernumber", "customername", "productcode",
    "quantityordered", "priceeach", "sales",
    "orderdate", "status", "dealsize"
]].copy()

orders = orders.merge(
    customers[["customer_id", "customer_name"]],
    left_on="customername",
    right_on="customer_name",
    how="left"
)

orders = orders.merge(
    products[["product_id", "product_code"]],
    left_on="productcode",
    right_on="product_code",
    how="left"
)

orders = orders[[
    "ordernumber", "customer_id", "product_id",
    "quantityordered", "priceeach", "sales",
    "orderdate", "status", "dealsize"
]]

orders.columns = [
    "order_number", "customer_id", "product_id",
    "quantity_ordered", "price_each", "sales",
    "order_date", "status", "deal_size"
]

# Fix date column
orders["order_date"] = pd.to_datetime(orders["order_date"])

# ---- Load into PostgreSQL ----
print("\n📤 Loading tables into PostgreSQL...")

customers.to_sql("customers", engine, if_exists="replace", index=False)
print(f"✅ customers table loaded — {len(customers)} rows")

products.to_sql("products", engine, if_exists="replace", index=False)
print(f"✅ products table loaded — {len(products)} rows")

orders.to_sql("orders", engine, if_exists="replace", index=False)
print(f"✅ orders table loaded — {len(orders)} rows")

print("\n🎉 All data loaded successfully!")
print("\nTables created:")
print("  - customers (customer info)")
print("  - products  (product catalog)")
print("  - orders    (transactions)")