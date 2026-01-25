import requests
import json

# URL of your local API
url = "http://127.0.0.1:5000/api/analyze"

# The coin we want to test (One that you definitely don't have yet)
payload = {"ticker": "DOGE-USD"}

print(f"Testing Backend with {payload['ticker']}...")

try:
    # Send the request to your backend
    response = requests.post(url, json=payload)
    
    # Print the result
    if response.status_code == 200:
        print("\n✅ SUCCESS! Backend is working 100%.")
        print("Received Data form Server:")
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"\n❌ FAILED. Status Code: {response.status_code}")
        print("Error message:", response.text)

except Exception as e:
    print(f"\n❌ CRITICAL ERROR: Could not connect to server. Is app.py running?")
    print(f"Details: {e}")