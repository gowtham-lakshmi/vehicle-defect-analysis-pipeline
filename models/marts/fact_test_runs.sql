{{ config(materialized='table') }}
select run_id, test_case_id, release_id, run_date, tester, result,
       execution_time_sec,
       case when result = 'Pass' then 1 else 0 end as is_pass,
       case when result = 'Fail' then 1 else 0 end as is_fail
from {{ ref('stg_test_runs') }}