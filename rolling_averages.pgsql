SELECT
  activities.date as time,
  round(cast((fairly_active_minutes+very_active_minutes) as decimal)/(sedentary_minutes+lightly_active_minutes+fairly_active_minutes+very_active_minutes)*100,2) AS "Activity Level",
  hr.resting_hr AS "Resting HR"
FROM activities
JOIN hr
ON hr.date = activities.date;

SELECT
    AVG(round(cast((fairly_active_minutes+very_active_minutes) as decimal)/(sedentary_minutes+lightly_active_minutes+fairly_active_minutes+very_active_minutes)*100,2)) as "Average Activity Level"
FROM activities;

-- Rolling averages
SELECT 
    activities.date AS time,  
    AVG(round(cast((fairly_active_minutes+very_active_minutes) as decimal)/(sedentary_minutes+lightly_active_minutes+fairly_active_minutes+very_active_minutes)*100,2)) OVER(ORDER BY activities.date ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS "Rolling Activity Level Average",
    AVG(round(cast(calories_activity as decimal)/(calories_total)*100,2)) OVER(ORDER BY activities.date ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS "Rolling Activity Calories Average",
    AVG(round(cast((hr.peak_minutes+hr.cardio_minutes+hr.fat_burn_minutes) as decimal)/(hr.peak_minutes+hr.cardio_minutes+hr.fat_burn_minutes+hr.out_of_range_minutes)*100,2)) OVER(ORDER BY activities.date ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS "Rolling Activity Minutes Average",
    AVG(hr.resting_hr) OVER(ORDER BY hr.date ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS "Rolling Resting HR Average",
    AVG(round(cast((total_rem_sleep_minutes+total_deep_sleep_minutes) as decimal)/(total_deep_sleep_minutes+total_light_sleep_minutes+total_rem_sleep_minutes+total_wake_minutes)*100,2)) OVER(ORDER BY sleep.date ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS "Rolling Sleep Quality Average",
    AVG(round(cast(sleep.total_asleep_minutes/60 as decimal),2)) OVER(ORDER BY sleep.date ROWS BETWEEN 7 PRECEDING AND CURRENT ROW) AS "Rolling Sleep Duration Average",
    sleep.total_sleep_recordings AS "Sleep Sessions"
FROM activities
JOIN hr ON hr.date = activities.date
JOIN sleep ON sleep.date = activities.date
WHERE (total_deep_sleep_minutes+total_light_sleep_minutes+total_rem_sleep_minutes+total_wake_minutes) > 0;


-- Average HR and Activity LEVEL
SELECT
    AVG(hr.resting_hr) as "Average Resting HR",
    AVG(activities.fairly_active_minutes+activities.very_active_minutes) as "Average Activity Level"
FROM activities
JOIN hr
ON hr.date = activities.date;

