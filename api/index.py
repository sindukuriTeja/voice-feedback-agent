import json


def handler(event, context):
    path = event.get("path", "/")
    h = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 204, "headers": h, "body": ""}
    if path == "/api/health":
        h["Content-Type"] = "application/json"
        return {"statusCode": 200, "headers": h, "body": json.dumps({"status": "ok"})}
    h["Content-Type"] = "text/html"
    return {"statusCode": 200, "headers": h, "body": "<html><body><h1>FeedbackBot Pro</h1><p>AI-Powered Voice Feedback System</p></body></html>"}