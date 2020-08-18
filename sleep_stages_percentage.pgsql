SELECT
  date as time,
  round(cast(total_deep_sleep_minutes as decimal)/(total_deep_sleep_minutes+total_light_sleep_minutes+total_rem_sleep_minutes+total_wake_minutes)*100,2) AS "Deep Sleep %",
  round(cast(total_light_sleep_minutes as decimal)/(total_deep_sleep_minutes+total_light_sleep_minutes+total_rem_sleep_minutes+total_wake_minutes)*100,2) AS "Light Sleep %",
  round(cast(total_rem_sleep_minutes as decimal)/(total_deep_sleep_minutes+total_light_sleep_minutes+total_rem_sleep_minutes+total_wake_minutes)*100,2) AS "Rem Sleep %",
  round(cast(total_wake_minutes as decimal)/(total_deep_sleep_minutes+total_light_sleep_minutes+total_rem_sleep_minutes+total_wake_minutes)*100,2) AS "Wake Sleep %"
FROM sleep
WHERE ((total_deep_sleep_minutes+total_light_sleep_minutes+total_rem_sleep_minutes+total_wake_minutes) > 0);