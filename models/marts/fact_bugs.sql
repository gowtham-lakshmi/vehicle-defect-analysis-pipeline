{{ config(materialized='table') }}
select bug_id, run_id, release_id, module, severity, status,
       opened_date, closed_date,
       datediff(closed_date, opened_date) as days_to_close
from {{ ref('stg_bugs') }}