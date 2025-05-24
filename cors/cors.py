def with_cors_headers(response: dict) -> dict:
    response.setdefault("headers", {})
    response["headers"].update({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    })
    return response
