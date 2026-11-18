{{ config(materialized='table') }}
select r.release_id, r.bike_id, b.model, b.variant,
       r.sw_version, r.release_date, r.release_type
from {{ ref('stg_releases') }} r
join {{ ref('stg_bikes') }} b on r.bike_id = b.bike_id