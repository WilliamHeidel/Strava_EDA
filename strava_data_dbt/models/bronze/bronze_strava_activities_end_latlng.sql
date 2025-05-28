
SELECT *
FROM {{ source('strava_rest_api_dataset','activities__end_latlng') }}
