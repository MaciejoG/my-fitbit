SELECT
  activities.date as time,
  round(cast((fairly_active_minutes+very_active_minutes) as decimal)/(sedentary_minutes+lightly_active_minutes+fairly_active_minutes+very_active_minutes)*100,2) AS "Activity Level",
  round(cast((total_rem_sleep_minutes+total_deep_sleep_minutes) as decimal)/(total_deep_sleep_minutes+total_light_sleep_minutes+total_rem_sleep_minutes+total_wake_minutes)*100,2) AS "Sleep Quality"
FROM activities
JOIN
    (
    SELECT 
        (sleep.date-1) AS date,
        sleep.total_rem_sleep_minutes,
        sleep.total_deep_sleep_minutes,
        sleep.total_light_sleep_minutes,
        sleep.total_wake_minutes
    FROM sleep
    ) sleep_lag 
ON sleep_lag.date = activities.date
WHERE (total_deep_sleep_minutes+total_light_sleep_minutes+total_rem_sleep_minutes+total_wake_minutes) > 0;
