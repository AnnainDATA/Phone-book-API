import requests

from config import TEST_USER_EMAIL, API_BASE_URL, TEST_USER_PASSWORD

payload = ({"username":TEST_USER_EMAIL, "password": TEST_USER_PASSWORD})
login = requests.post(f"{API_BASE_URL}/v1/user/login/usernamepassword", json=payload)
token = login.json()["token"]