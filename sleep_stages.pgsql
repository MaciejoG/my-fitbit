SELECT
  date as time,
  total_deep_sleep_minutes::decimal/60 AS "Deep Sleep",
  total_light_sleep_minutes::decimal/60 AS "Light Sleep",
  total_rem_sleep_minutes::decimal/60 AS "Rem Sleep",
  total_wake_minutes::decimal/60 AS "Wake Sleep"
FROM sleep
WHERE ((total_deep_sleep_minutes+total_light_sleep_minutes+total_rem_sleep_minutes+total_wake_minutes) > 0);