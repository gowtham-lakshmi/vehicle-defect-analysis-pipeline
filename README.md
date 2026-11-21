# Vehicle Defect Analysis Pipeline

A data engineering project that follows **software testing of a two-wheeler instrument cluster** (the dashboard that shows speed, fuel, warning lamps, Bluetooth alerts, etc.) from raw data to analysis-ready tables.

> **Note:** The data is **simulated** with Python. No real company data is used.
> I built this project to learn data engineering, with help from AI tools (Claude, ChatGPT and Gemini) for guidance and code review.

## What is this project about? (in simple words)

A bike company builds new software for its dashboard. Before the software goes to customers, testers run many tests on it. Some tests **pass**, some **fail**, and every failed test can create a **bug**.

This project stores all of that test data and helps answer questions like:

- Do software versions get better over time (Alpha → Beta → Production)?
- Which dashboard module (speedometer, Bluetooth, warning lamps...) has the most bugs?
- How many bugs are serious, and how many are still not fixed?

## Tools used

| Tool | What I used it for |
|---|---|
| VS Code | Writing and running the Python scripts |
| Python (pandas) | Generating the fake data and cleaning it |
| MySQL (Workbench) | Storing the clean data in 5 related tables. I used MySQL Workbench to create the tables and run SQL queries |
| AWS S3 | Storing the csv files in the cloud (raw and clean folders) |
| AWS IAM | Creating a user with limited permissions, so my tools can reach S3 safely |
| AWS Glue | A crawler scans the files in S3 and creates tables automatically, and a Spark ETL job processes them |
| Spark | Writing code to process the data |
| Databricks | Running Spark code, and the warehouse that dbt connects to |
| dbt (dbt Cloud) | Building staging and mart tables, with tests to check the data |
| Git and GitHub | Saving my code, using branches and pull requests |
| Power BI | A dashboard on top of the Databricks mart tables (bugs by module, release type and model, and pass rate) |

## How I built it (step by step)

```
VS Code + Python      generate data -> clean data
        |
     MySQL            load the clean tables, check them with SQL
        |
     AWS S3           upload the files (IAM user for access)
        |
  AWS Glue crawler    scan S3 and create tables
        |
 Spark + Databricks   process the data
        |
       dbt            staging models -> mart models -> tests
        |
     Power BI         dashboard (last step)
```

1. **Generate and clean the data.** I wrote the Python scripts in VS Code. The first script makes fake test data, the second cleans it with pandas.
2. **Load into MySQL.** I created the 5 tables in MySQL Workbench (`sql/create_tables.sql`), loaded the clean data with a Python script, and ran SQL queries to check the row counts and joins.
3. **Upload to AWS S3.** I created an IAM user with only the permissions it needs, and used it to put the csv files in S3.
4. **Make tables with Glue.** I ran Glue crawlers on the S3 folders, so Glue could read the files and create tables for me.
5. **Spark and Databricks.** I wrote Spark code to process the data and worked in Databricks.
6. **Transform with dbt.** I connected dbt to Databricks and built staging models, then mart models, and added tests to catch bad data.
7. **Save the work on GitHub.** I used Git to commit my code and a pull request to merge my branch into main.
8. **Dashboard in Power BI.** I connected Power BI to Databricks and built a dashboard from the mart tables. It shows total bikes, releases and bugs, bugs by module, bugs by release type and model, and the average pass rate for Alpha, Beta and Production.

## Dashboard

![Power BI dashboard](images/dashboard.png)

## The data: 5 tables explained

### How the tables connect

```
bikes  --(1 bike has many)-->  releases  --(1 release has many)-->  test_runs  --(a failed run can create)-->  bugs
                                                                        ^
                                              test_cases --(1 test case is run many times)
```

Think of it like this: **a bike** gets **software releases**. Each release is tested by running **test cases**. Every execution is a **test run**. If a run fails, a **bug** may be raised.

### 1. bikes (8 rows): the vehicles

| Column | Meaning | Example |
|---|---|---|
| bike_id | Unique number of the bike | 4 |
| model | Bike model | Scooter 125 |
| variant | Version of that model | Smart |
| cluster_type | Dashboard display type | TFT |

### 2. releases (32 rows): software versions

Each bike has 4 releases: Alpha, Beta, Beta, Production.

| Column | Meaning | Example |
|---|---|---|
| release_id | Unique number of the release | 1 |
| bike_id | Which bike this software is for | 1 |
| sw_version | Software version | v1.0 |
| release_date | Date released for testing | 2025-02-19 |
| release_type | Alpha = early, Beta = middle, Production = final | Alpha |

### 3. test_cases (30 rows): what we test

| Column | Meaning | Example |
|---|---|---|
| test_case_id | Unique number of the test | 7 |
| module | Part of the dashboard being tested | Fuel Gauge |
| title | Name of the test | Fuel level display |
| priority | How important (High / Medium / Low) | High |
| test_type | Functional or Regression | Regression |

### 4. test_runs (20,107 rows): every test execution

| Column | Meaning | Example |
|---|---|---|
| run_id | Unique number of the run | 3 |
| test_case_id | Which test was run | 23 |
| release_id | On which software release | 1 |
| run_date | Date of the run | 2025-02-25 |
| tester | Who ran it | Divya |
| result | Pass, Fail or Blocked | Fail |
| execution_time_sec | Seconds taken | 484 |

### 5. bugs (2,148 rows): problems found

| Column | Meaning | Example |
|---|---|---|
| bug_id | Unique number of the bug | 1 |
| run_id | The failed run that found it | 3 |
| release_id | The software release | 1 |
| module | Dashboard module with the problem | Display |
| severity | Critical, Major or Minor | Critical |
| status | Open, In Progress or Closed | Open |
| opened_date | Date the bug was raised | 2025-02-25 |
| closed_date | Date it was fixed (empty if not fixed) | 2025-03-21 |

## Data cleaning (clean_data.py)

The raw data has some problems added on purpose, to practice cleaning:

| Problem found | What I did |
|---|---|
| 10 duplicate rows in test_runs | Removed them |
| Result written as PASS / Pass / FAIL / Fail | Made all the same style (Pass, Fail, Blocked) |
| 5 negative execution times (not possible) | Treated as missing |
| About 200 missing execution times | Filled with the median time of the same test case |
| Dates stored as text | Converted to real dates |
| Broken links between tables | Checked that every id exists in its parent table (all passed) |

Result: 20,117 raw rows in test_runs became 20,107 clean rows.

## Key findings (from the clean data)

- **Software gets better with each stage.** Test fail rate: Alpha **28%**, Beta **14%**, Production **4.5%**.
- **Bugs drop sharply in Production.** Average bugs per release: Alpha about 123, Beta about 63, Production about 20.
- **Warning Lamps has the most bugs** (303), then UDS Diagnostics (234) and Fuel Gauge (220). Odometer has the fewest (149).
- **Severity:** 1,056 Minor, 878 Major, 214 Critical bugs.
- **Fix status:** 1,484 bugs (69%) are Closed, 335 are Open and 329 are In Progress.

## Folder structure

```
vehicle-defect-analysis-pipeline
├── models/      dbt models (staging and mart)
├── tests/       dbt tests
├── scripts/     python scripts (generate, clean, load)
├── sql/         create_tables.sql (MySQL table definitions)
├── images/      dashboard screenshot
└── data/
    ├── raw/     raw csv files
    └── clean/   cleaned csv files
```

## How to run

Run all commands from the project root folder.

1. In MySQL Workbench, run `sql/create_tables.sql` to create the database and the 5 tables.
2. Then run these in a terminal:

```
pip install pandas mysql-connector-python
python scripts/generate_data.py
python scripts/clean_data.py
python scripts/load_to_mysql.py
```

`load_to_mysql.py` asks for your MySQL password when it runs, so no password is stored in the code.
The database name is `cluster_defect_db`. The dbt models run on Databricks (see the `models/` folder).

## Author

Gowtham M
[LinkedIn](https://www.linkedin.com/in/gowtham-lakshmi-7228b6409)
