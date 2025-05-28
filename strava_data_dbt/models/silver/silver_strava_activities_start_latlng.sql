
SELECT 
    _dlt_parent_id
    ,MAX(CASE WHEN _dlt_list_idx = 0 THEN value ELSE NULL END) AS start_lat
    ,MAX(CASE WHEN _dlt_list_idx = 1 THEN value ELSE NULL END) AS start_long
FROM {{ ref('bronze_strava_activities_start_latlng') }}
GROUP BY _dlt_parent_id
