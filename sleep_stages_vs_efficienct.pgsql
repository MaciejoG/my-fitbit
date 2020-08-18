SELECT
  date as time,
  total_in_bed_minutes::decimal/60 AS "In Bed",
  total_asleep_minutes::decimal/60 AS "Asleep",
  total_awake_minutes::decimal/60 AS "Awake",
  total_sleep_efficiency::decimal*100 AS "Sleep Efficiency"
FROM sleep;