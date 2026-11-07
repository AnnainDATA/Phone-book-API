from dataclasses import asdict
import pytest
import requests
from config import API_BASE_URL
from models.user import User


def test_registration_success(new_user):
    payload = asdict(new_user)
    response=requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "token" in body
    assert len(body["token"])>0


def test_registration_invalid_email_rejected(new_user):
    payload = asdict(new_user)
    response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert "username" in response.json()["message"]
    body = response.json()
    assert body["status"] == 400
    assert response.json()["error"] == "Bad Request"
    assert body["path"] == "/v1/user/registration/usernamepassword"


def test_registration_password_without_uppercase_rejected(new_user):
    payload = asdict(new_user)
    response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert "password" in response.json()["message"]


def test_registration_password_too_short_rejected(new_user):
    payload = asdict(new_user)
    response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert "password" in response.json()["message"]


@pytest.mark.parametrize(
    "field,bad_value", [
        pytest.param("password", "Pass12$", id="password_too_short"),
        pytest.param("password", "password123$", id="password_no_uppercase"),
        pytest.param("password", "PASSWORD123$", id="password_no_lowercase"),
        pytest.param("password", "PASSWORD$", id="password_no_digits"),
        pytest.param("password", "Password123", id="password_no_special_char"),
        pytest.param("password", "PASSWORD123$fddgjhdkfjhfdkhj", id="password_too_long"),
        pytest.param("username", "user@", id="username_no_domain"),
        pytest.param("username", "notanemail", id="username_no_at_sign"),
        pytest.param("username", "@gmail.com", id="username_no_local_part"),
        pytest.param("username", "", id="username_empty")
            ])
def test_registration_with_invalid_value_rejected(new_user,field,bad_value):
    payload =asdict(new_user)
    payload[field]=bad_value
    response=requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert field in response.json()["message"]
    assert "token" not in response.json()


@pytest.mark.parametrize("missing_field",["username","password"])
def test_registration_missing_field(new_user,missing_field):
    payload = asdict(new_user)
    del payload[missing_field]
    response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert missing_field in response.json()["message"]


def test_registration_with_empty_password_rejected(unique_email):
    payload = asdict(User(username=unique_email,password=""))
    response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == "Bad Request"


def test_registration_duplicate_user_rejected(new_user):
    payload = asdict(new_user)
    first_response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert first_response.status_code == 200

    second_response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert second_response.status_code == 409
    assert "User already exists" in second_response.json()["message"]
    assert second_response.json()["error"] == "Conflict"
    assert second_response.json()["path"] == "/v1/user/registration/usernamepassword"


def test_registered_user_new_password_rejected(new_user):
    payload = asdict(new_user)  #registration with walid data
    print(payload)
    first_response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload)
    assert first_response.status_code == 200

    payload1 = asdict(User(username=new_user.username, password="An7777777!")) #registration with the same email and new pwd
    print(payload1)
    second_response = requests.post(f"{API_BASE_URL}/v1/user/registration/usernamepassword", json=payload1)
    assert second_response.status_code == 409
    assert "User already exists" in second_response.json()["message"]
    assert second_response.json()["error"] == "Conflict"
    assert second_response.json()["path"] == "/v1/user/registration/usernamepassword"