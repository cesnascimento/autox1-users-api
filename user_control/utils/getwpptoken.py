import requests


def getwpptoken(session: str) -> str:
  response = requests.post(f'http://localhost:21465/api/{session}/THISISMYSECURETOKEN/generate-token').json()
  if response['status'] == 'success':
    token = response['token']
    return token