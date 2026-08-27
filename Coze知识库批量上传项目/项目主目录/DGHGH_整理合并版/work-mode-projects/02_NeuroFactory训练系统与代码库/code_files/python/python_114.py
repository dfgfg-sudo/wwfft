import requests

url = "https://api.aiworkflowplatform.com/v1/operations/execute"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}
payload = {
    "operation_mode": "emergency_activation",
    "input_data": {
        "emergency_type": "system_failure",
        "severity": "critical",
        "recovery_priority": "high",
        "affected_components": ["database", "api_gateway"],
        "automatic_recovery": True
    }
}
response = requests.post(url, json=payload, headers=headers)
print(response.json())