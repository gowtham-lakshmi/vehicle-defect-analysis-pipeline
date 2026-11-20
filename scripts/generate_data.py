# generate_data.py
# Makes fake (simulated) data for a two-wheeler cluster software defect project.
# Output: 5 raw csv files in data/raw/
# Run from the project root folder:  python scripts/generate_data.py

import os
import random
from datetime import date, timedelta
import pandas as pd

random.seed(42)
os.makedirs("data/raw", exist_ok=True)


# bikes table
bike_rows = [
    (1, "Commuter 110", "Base", "Segment LCD"),
    (2, "Commuter 110", "Top", "Digital LCD"),
    (3, "Scooter 125", "Standard", "Digital LCD"),
    (4, "Scooter 125", "Smart", "TFT"),
    (5, "Sport 160", "Standard", "Digital LCD"),
    (6, "Sport 160", "Pro", "TFT"),
    (7, "Adventure 200", "Standard", "TFT"),
    (8, "Electric E1", "Standard", "TFT"),
]
bikes = pd.DataFrame(bike_rows, columns=["bike_id", "model", "variant", "cluster_type"])


# releases table 
# every bike gets 4 software releases: Alpha -> Beta -> Beta -> Production
release_types = ["Alpha", "Beta", "Beta", "Production"]
release_rows = []
release_id = 1
first_date = date(2025, 1, 10)

for bike_id in bikes["bike_id"]:
    release_date = first_date + timedelta(days=random.randint(0, 40))
    for number, release_type in enumerate(release_types, start=1):
        version = f"v{number}.{random.randint(0, 3)}"
        release_rows.append((release_id, bike_id, version, release_date.isoformat(), release_type))
        release_id += 1
        release_date = release_date + timedelta(days=random.randint(30, 75))

releases = pd.DataFrame(
    release_rows,
    columns=["release_id", "bike_id", "sw_version", "release_date", "release_type"],
)


# test_cases table
# cluster modules and the tests we run on each one
modules = {
    "Speedometer": ["Speed display accuracy", "Speed unit switch", "Over-speed warning"],
    "Tachometer": ["RPM needle response", "Redline indication", "RPM at idle"],
    "Fuel Gauge": ["Fuel level display", "Low fuel warning", "Fuel bar flicker"],
    "Warning Lamps": ["Engine lamp", "ABS lamp", "Side stand lamp", "Battery lamp"],
    "Odometer": ["Odometer increment", "Odometer power cycle retain"],
    "Trip Meter": ["Trip A reset", "Trip B reset", "Trip auto reset"],
    "Bluetooth": ["Phone pairing", "Call alert display", "SMS alert display"],
    "Display": ["Brightness auto adjust", "Day night mode", "Startup animation"],
    "CAN Communication": ["CAN message timeout", "CAN signal validity", "Bus off recovery"],
    "UDS Diagnostics": ["Read DTC", "Clear DTC", "Session control"],
}

test_case_rows = []
test_case_id = 1
for module_name, test_titles in modules.items():
    for title in test_titles:
        priority = random.choice(["High", "High", "Medium", "Low"])
        test_type = random.choice(["Functional", "Regression", "Regression"])
        test_case_rows.append((test_case_id, module_name, title, priority, test_type))
        test_case_id += 1

test_cases = pd.DataFrame(
    test_case_rows,
    columns=["test_case_id", "module", "title", "priority", "test_type"],
)


# test_runs table
# early releases (Alpha) fail more, Production fails very little
testers = ["Arun", "Divya", "Karthik", "Meena", "Suresh", "Priya"]
fail_chance = {"Alpha": 0.28, "Beta": 0.14, "Production": 0.04}

run_rows = []
run_id = 1
for _, rel in releases.iterrows():
    start_date = date.fromisoformat(rel["release_date"])
    p_fail = fail_chance[rel["release_type"]]
    runs_in_release = random.randint(560, 690)

    for _ in range(runs_in_release):
        test_case = test_cases.sample(1).iloc[0]

        r = random.random()
        if r < p_fail:
            result = "Fail"
        elif r < p_fail + 0.03:
            result = "Blocked"
        else:
            result = "Pass"

        run_date = start_date + timedelta(days=random.randint(0, 14))
        tester = random.choice(testers)
        exec_time = random.randint(20, 600)

        run_rows.append((run_id, int(test_case["test_case_id"]), int(rel["release_id"]),
                         run_date.isoformat(), tester, result, exec_time))
        run_id += 1

test_runs = pd.DataFrame(
    run_rows,
    columns=["run_id", "test_case_id", "release_id", "run_date",
             "tester", "result", "execution_time_sec"],
)


# bugs table
# a bug is raised for about 70% of the failed runs
failed_runs = test_runs[test_runs["result"] == "Fail"]
module_of_test = dict(zip(test_cases["test_case_id"], test_cases["module"]))

bug_rows = []
bug_id = 1
for _, run in failed_runs.iterrows():
    if random.random() < 0.7:
        opened_date = date.fromisoformat(run["run_date"])
        status = random.choices(["Closed", "Open", "In Progress"], weights=[70, 15, 15])[0]

        closed_date = None
        if status == "Closed":
            closed_date = (opened_date + timedelta(days=random.randint(1, 20))).isoformat()

        severity = random.choices(["Critical", "Major", "Minor"], weights=[10, 40, 50])[0]
        module_name = module_of_test[run["test_case_id"]]

        bug_rows.append((bug_id, int(run["run_id"]), int(run["release_id"]), module_name,
                         severity, status, opened_date.isoformat(), closed_date))
        bug_id += 1

bugs = pd.DataFrame(
    bug_rows,
    columns=["bug_id", "run_id", "release_id", "module", "severity",
             "status", "opened_date", "closed_date"],
)


# add some dirty data on purpose, so we can practice cleaning

# 1% missing execution time
rows = test_runs.sample(frac=0.01, random_state=1).index
test_runs.loc[rows, "execution_time_sec"] = None

# 1% results in capital letters (PASS, FAIL)
rows = test_runs.sample(frac=0.01, random_state=2).index
test_runs.loc[rows, "result"] = test_runs.loc[rows, "result"].str.upper()

# 5 rows with negative execution time (invalid)
rows = test_runs.sample(n=5, random_state=3).index
test_runs.loc[rows, "execution_time_sec"] = -1

# 10 duplicate rows
duplicates = test_runs.sample(n=10, random_state=4)
test_runs = pd.concat([test_runs, duplicates], ignore_index=True)


# save all tables as csv
all_tables = {
    "bikes": bikes,
    "releases": releases,
    "test_cases": test_cases,
    "test_runs": test_runs,
    "bugs": bugs,
}
for name, table in all_tables.items():
    table.to_csv(f"data/raw/{name}.csv", index=False)
    print(name, "->", len(table), "rows saved")
