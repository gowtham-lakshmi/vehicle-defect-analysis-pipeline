select release_id, bike_id, sw_version,
       cast(release_date as date) as release_date, release_type
from {{ source('raw', 'releases_delta') }}