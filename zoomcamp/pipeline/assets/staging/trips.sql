/* @bruin

name: staging.trips

type: duckdb.sql

depends:
  - ingestion.trips
  - ingestion.payment_lookup

materialization:
  type: table
  strategy: time_interval
  incremental_key: pickup_datetime
  time_granularity: timestamp

columns:
  - name: taxi_type
    type: string
    description: Taxi type (yellow or green)
    primary_key: false
    nullable: false
    checks:
      - name: not_null
  - name: pickup_datetime
    type: timestamp
    description: Pickup date and time
    primary_key: false
    nullable: false
    checks:
      - name: not_null
  - name: dropoff_datetime
    type: timestamp
    description: Dropoff date and time
    nullable: false
    checks:
      - name: not_null
  - name: passenger_count
    type: double
    description: Number of passengers
    checks:
      - name: non_negative
  - name: trip_distance
    type: double
    description: Trip distance in miles
    checks:
      - name: non_negative
  - name: pulocationid
    type: integer
    description: Pickup location (TLC zone) ID
  - name: dolocationid
    type: integer
    description: Dropoff location (TLC zone) ID
  - name: payment_type
    type: integer
    description: Payment type code
    checks:
      - name: not_null
  - name: payment_type_name
    type: string
    description: Payment type name from lookup
  - name: total_amount
    type: double
    description: Total amount charged
    checks:
      - name: non_negative

custom_checks:
  - name: staging_trips_no_duplicate_key
    description: No duplicate (taxi_type, pickup_datetime, pulocationid, dolocationid) in window
    query: |
      SELECT COUNT(*) - COUNT(DISTINCT (taxi_type, pickup_datetime, pulocationid, dolocationid))
      FROM staging.trips
      WHERE pickup_datetime >= '{{ start_datetime }}' AND pickup_datetime < '{{ end_datetime }}'
    value: 0

@bruin */

WITH raw_window AS (
  SELECT
    taxi_type,
    pickup_datetime,
    dropoff_datetime,
    passenger_count,
    trip_distance,
    pulocationid,
    dolocationid,
    payment_type,
    total_amount,
    ROW_NUMBER() OVER (
      PARTITION BY taxi_type, pickup_datetime, pulocationid, dolocationid
      ORDER BY dropoff_datetime, total_amount
    ) AS rn
  FROM ingestion.trips
  WHERE pickup_datetime >= '{{ start_datetime }}'
    AND pickup_datetime < '{{ end_datetime }}'
),
deduped AS (
  SELECT
    taxi_type,
    pickup_datetime,
    dropoff_datetime,
    passenger_count,
    trip_distance,
    pulocationid,
    dolocationid,
    payment_type,
    total_amount
  FROM raw_window
  WHERE rn = 1
)
SELECT
  d.taxi_type,
  d.pickup_datetime,
  d.dropoff_datetime,
  d.passenger_count,
  d.trip_distance,
  d.pulocationid,
  d.dolocationid,
  d.payment_type,
  COALESCE(p.payment_type_name, 'unknown') AS payment_type_name,
  d.total_amount
FROM deduped d
LEFT JOIN ingestion.payment_lookup p ON p.payment_type_id = d.payment_type
