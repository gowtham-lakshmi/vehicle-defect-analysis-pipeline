select bug_id, run_id, release_id, module, severity, status,
       cast(opened_date as date) as opened_date,
       cast(closed_date as date) as closed_date
from {{ source('raw', 'bugs_delta') }}