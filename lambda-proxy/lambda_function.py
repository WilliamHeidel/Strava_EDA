import os, json, boto3

# Environment variables set in Lambda configuration
env = os.environ
CLUSTER_ID = env["CLUSTER_ID"]
DATABASE   = env["DATABASE"]
DB_USER    = env["DB_USER"]

# Initialize Redshift Data API client with explicit region
client = boto3.client(
    "redshift-data",
    region_name=env.get("AWS_REGION", "us-east-2")
)

def handler(event, context):
    # Construct SQL (could be parameterized via event)
    sql = "SELECT * FROM strava_rest_api_dataset.activities"

    # Execute the statement
    exec_resp = client.execute_statement(
        ClusterIdentifier=CLUSTER_ID,
        Database=DATABASE,
        DbUser=DB_USER,
        Sql=sql
    )
    stmt_id = exec_resp["Id"]

    # Poll until the statement completes
    while True:
        desc = client.describe_statement(Id=stmt_id)
        status = desc["Status"]
        if status in ("FAILED", "ABORTED"):
            raise RuntimeError(f"Query failed: {desc.get('Error')}")
        if status == "FINISHED":
            break

    # Fetch the first page of results
    result = client.get_statement_result(Id=stmt_id)
    cols = [col["name"] for col in result["ColumnMetadata"]]
    records = result.get("Records", [])
    next_token = result.get("NextToken")

    # Fetch additional pages if present
    while next_token:
        page = client.get_statement_result(
            Id=stmt_id,
            NextToken=next_token
        )
        records.extend(page.get("Records", []))
        next_token = page.get("NextToken")

    # Parse records into list of dicts
    rows = []
    for rec in records:
        row = {}
        for i, field in enumerate(rec):
            # Handle various Data API types
            if "stringValue" in field:
                v = field["stringValue"]
            elif "longValue" in field:
                v = field["longValue"]
            elif "doubleValue" in field:
                v = field["doubleValue"]
            elif "booleanValue" in field:
                v = field["booleanValue"]
            elif "arrayValue" in field:
                v = [x for x in field["arrayValue"]["values"]]
            else:
                v = None
            row[cols[i]] = v
        rows.append(row)

    # Return the full JSON response with CORS
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(rows)
    }
