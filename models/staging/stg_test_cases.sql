select test_case_id, module, title, priority, test_type
from {{ source('raw', 'test_cases_delta') }}