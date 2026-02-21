{{ config(materialized='view') }}

with tripdata as 
(
  select *
  from {{ source('raw','fhv_tripdata') }}
  where dispatching_base_num is not null --parameter to filter out bad data
)
select
    dispatching_base_num,
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,
    cast(pulocationid as integer) as pickup_location_id,
    cast(dolocationid as integer) as dropoff_location_id,
    sr_flag,
    affiliated_base_number
from tripdata