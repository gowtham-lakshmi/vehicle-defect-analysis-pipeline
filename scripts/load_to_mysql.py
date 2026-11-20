# load_to_mysql.py
# Loads the clean csv files into MySQL tables.
# Run from the project root folder:  python scripts/load_to_mysql.py

import pandas as pd
import mysql.connector

# parent tables first, child tables after (because of foreign keys)
tables = ["bikes", "releases", "test_cases", "test_runs", "bugs"]

# password is typed at run time, so it is never saved in the code
password = input("Enter MySQL password: ")

print("Connecting to MySQL...")
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="cluster_defect_db",
    connection_timeout=10,
)
cursor = connection.cursor()
print("Connected")

# delete old rows first (child tables first), so running again is safe
for table in reversed(tables):
    cursor.execute(f"DELETE FROM {table}")
connection.commit()

# load each clean csv into its table
for table in tables:
    df = pd.read_csv(f"data/clean/{table}/{table}.csv")

    # MySQL needs None instead of NaN for empty values
    df = df.astype(object).where(df.notnull(), None)

    columns = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    cursor.executemany(insert_sql, df.values.tolist())
    connection.commit()
    print(table, "->", len(df), "rows loaded")

# final check: count rows inside MySQL
print("\nRow count in MySQL:")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    print(table, "->", cursor.fetchone()[0])

cursor.close()
connection.close()
