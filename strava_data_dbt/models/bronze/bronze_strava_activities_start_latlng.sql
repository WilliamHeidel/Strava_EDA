
SELECT *
FROM {{ source('strava_rest_api_dataset','activities__start_latlng') }}
