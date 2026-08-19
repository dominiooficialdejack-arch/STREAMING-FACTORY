import os
import requests

url = os.getenv('PUBLIC_APP_URL', 'https://streaming-factory.onrender.com')
response = requests.get(url.rstrip('/') + '/api/health', timeout=45)
print('keepalive', response.status_code, response.text[:300])
response.raise_for_status()
