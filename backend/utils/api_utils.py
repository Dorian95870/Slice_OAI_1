import requests

def send_request_to_nsmf(slice):
    url = 'http://localhost:8000/nsmf/api/slice'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=slice.__dict__, headers=headers)
    return response.json()
