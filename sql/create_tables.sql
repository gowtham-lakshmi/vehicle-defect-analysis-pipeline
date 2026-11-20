-- Creates the MySQL database and the 5 tables used in this project.
-- Run it in MySQL Workbench before loading the data.

DROP DATABASE IF EXISTS cluster_defect_db;
CREATE DATABASE cluster_defect_db;
USE cluster_defect_db;

CREATE TABLE bikes (
  bike_id INT PRIMARY KEY,
  model VARCHAR(50),
  variant VARCHAR(30),
  cluster_type VARCHAR(30)
);

CREATE TABLE releases (
  release_id INT PRIMARY KEY,
  bike_id INT,
  sw_version VARCHAR(10),
  release_date DATE,
  release_type VARCHAR(20),
  FOREIGN KEY (bike_id) REFERENCES bikes(bike_id)
);

CREATE TABLE test_cases (
  test_case_id INT PRIMARY KEY,
  module VARCHAR(50),
  title VARCHAR(100),
  priority VARCHAR(10),
  test_type VARCHAR(20)
);

CREATE TABLE test_runs (
  run_id INT PRIMARY KEY,
  test_case_id INT,
  release_id INT,
  run_date DATE,
  tester VARCHAR(30),
  result VARCHAR(10),
  execution_time_sec INT,
  FOREIGN KEY (test_case_id) REFERENCES test_cases(test_case_id),
  FOREIGN KEY (release_id) REFERENCES releases(release_id)
);

CREATE TABLE bugs (
  bug_id INT PRIMARY KEY,
  run_id INT,
  release_id INT,
  module VARCHAR(50),
  severity VARCHAR(10),
  status VARCHAR(20),
  opened_date DATE,
  closed_date DATE NULL,
  FOREIGN KEY (run_id) REFERENCES test_runs(run_id),
  FOREIGN KEY (release_id) REFERENCES releases(release_id)
);
