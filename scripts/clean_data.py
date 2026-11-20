# clean_data.py
# Cleans the raw csv files using pandas.
# Input : data/raw/<table>.csv
# Output: data/clean/<table>/<table>.csv
# Run from the project root folder:  python scripts/clean_data.py

import os
import pandas as pd

table_names = ["bikes", "releases", "test_cases", "test_runs", "bugs"]

# read all raw files
bikes = pd.read_csv("data/raw/bikes.csv")
releases = pd.read_csv("data/raw/releases.csv")
test_cases = pd.read_csv("data/raw/test_cases.csv")
test_runs = pd.read_csv("data/raw/test_runs.csv")
bugs = pd.read_csv("data/raw/bugs.csv")


def show_summary(title):
    # prints the quality numbers of test_runs, used before and after cleaning
    print(title)
    print("rows                :", len(test_runs))
    print("duplicate rows      :", test_runs.duplicated().sum())
    print("missing exec time   :", test_runs["execution_time_sec"].isna().sum())
    print("negative exec time  :", (test_runs["execution_time_sec"] < 0).sum())
    print("result values       :", sorted(test_runs["result"].unique()))


show_summary("=== BEFORE CLEANING ===")

# step 1: remove duplicate rows
test_runs = test_runs.drop_duplicates()

# step 2: make result values same case (PASS -> Pass)
test_runs["result"] = test_runs["result"].str.strip().str.title()

# step 3: negative time is not possible, so make it missing
test_runs.loc[test_runs["execution_time_sec"] < 0, "execution_time_sec"] = None

# step 4: fill missing time with the median time of the same test case
median_time = test_runs.groupby("test_case_id")["execution_time_sec"].transform("median")
test_runs["execution_time_sec"] = test_runs["execution_time_sec"].fillna(median_time)
test_runs["execution_time_sec"] = test_runs["execution_time_sec"].round().astype(int)

# step 5: convert text dates to real dates
test_runs["run_date"] = pd.to_datetime(test_runs["run_date"])
bugs["opened_date"] = pd.to_datetime(bugs["opened_date"])
bugs["closed_date"] = pd.to_datetime(bugs["closed_date"])
releases["release_date"] = pd.to_datetime(releases["release_date"])

# step 6: check foreign keys (every id must exist in its parent table)
assert test_runs["release_id"].isin(releases["release_id"]).all(), "wrong release_id in test_runs"
assert test_runs["test_case_id"].isin(test_cases["test_case_id"]).all(), "wrong test_case_id in test_runs"
assert bugs["run_id"].isin(test_runs["run_id"]).all(), "wrong run_id in bugs"
assert releases["bike_id"].isin(bikes["bike_id"]).all(), "wrong bike_id in releases"

print()
show_summary("=== AFTER CLEANING ===")
print("foreign key checks  : PASSED")

# save clean files as data/clean/<table>/<table>.csv
clean_tables = {
    "bikes": bikes,
    "releases": releases,
    "test_cases": test_cases,
    "test_runs": test_runs,
    "bugs": bugs,
}
for name, table in clean_tables.items():
    os.makedirs(f"data/clean/{name}", exist_ok=True)
    table.to_csv(f"data/clean/{name}/{name}.csv", index=False)

print("\nSaved", len(clean_tables), "clean files in data/clean/")
