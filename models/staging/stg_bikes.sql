select bike_id, model, variant, cluster_type
from {{ source('raw', 'bikes_delta') }}