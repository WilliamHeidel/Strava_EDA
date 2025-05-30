
SELECT *
    ,[distance] / 1609.344 AS distance_miles
    ,CAST([moving_time] AS float) / 60 AS moving_time_minutes
    ,CAST([moving_time] AS float) / 3600 AS moving_time_hours
    ,CAST([elapsed_time] AS float) / 60 AS elapsed_time_minutes
    ,CAST([elapsed_time] AS float) / 3600 AS elapsed_time_hours
    ,CAST([start_date] AS date) AS start_date_datevalue
    ,CAST([start_date_local] AS date) AS start_date_local_datevalue
FROM {{ ref('bronze_strava_activities') }}
