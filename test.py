import requests
import json
headers = {'code' : 'for i in range(10):print(i)'}
response = requests.get('http://192.168.0.163:8000/python', headers = headers)

print(response.content)