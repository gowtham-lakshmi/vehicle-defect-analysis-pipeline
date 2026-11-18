select run_id, test_case_id, release_id,
       cast(run_date as date) as run_date,
       tester, result, execution_time_sec
from {{ source('raw', 'test_runs_delta') }}