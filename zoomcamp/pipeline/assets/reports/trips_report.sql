/* @bruin

name: reports.trips_report

type: duckdb.sql

depends:
  - staging.trips

materialization:
  type: table
  strategy: time_interval
  incremental_key: trip_date
  time_granularity: date

columns:
  - name: trip_date
    type: date
    description: Date of trip (from pickup)
    primary_key: true
  - name: taxi_type
    type: string
    description: Taxi type (yellow or green)
    primary_key: true
  - name: payment_type_name
    type: string
    description: Payment type name
    primary_key: true
  - name: trip_count
    type: BIGINT
    description: Number of trips
    checks:
      - name: non_negative
  - name: total_passengers
    type: BIGINT
    description: Sum of passenger_count
    checks:
      - name: non_negative
  - name: total_amount
    type: double
    description: Sum of total_amount
    checks:
      - name: non_negative

@bruin */

SELECT
  CAST(pickup_datetime AS DATE) AS trip_date,
  taxi_type,
  payment_type_name,
  COUNT(*) AS trip_count,
  SUM(CAST(COALESCE(passenger_count, 0) AS BIGINT)) AS total_passengers,
  SUM(COALESCE(total_amount, 0)) AS total_amount
FROM staging.trips
WHERE pickup_datetime >= '{{ start_datetime }}'
  AND pickup_datetime < '{{ end_datetime }}'
GROUP BY
  CAST(pickup_datetime AS DATE),
  taxi_type,
  payment_type_name
