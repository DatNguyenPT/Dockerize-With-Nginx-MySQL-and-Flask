import requests

# The API endpoint
url = "http://localhost:8080/welcome"

print("Number of requests: ")
numberOfRequest = int(input())

for i in range(numberOfRequest):
    # A GET request to the API
    response = requests.get(url)
    response_json = response.json()
    print(response_json)
