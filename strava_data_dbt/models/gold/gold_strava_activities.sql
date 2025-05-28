
SELECT act.*
    ,st.start_lat
    ,st.start_long
    ,ed.end_lat
    ,ed.end_long
FROM {{ ref('silver_strava_activities') }} act
FULL OUTER JOIN {{ ref('silver_strava_activities_start_latlng') }} st
    ON st._dlt_parent_id = act._dlt_id
FULL OUTER JOIN {{ ref('silver_strava_activities_end_latlng') }} ed
    ON ed._dlt_parent_id = act._dlt_id
