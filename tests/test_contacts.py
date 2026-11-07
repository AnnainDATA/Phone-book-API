from dataclasses import asdict

import pytest
import requests
from config import *
from models.contact import fake, Contact
from models.user import User


def test_get_contacts_without_token_rejected():
    response = requests.get(f"{API_BASE_URL}/v1/contacts")
    assert response.status_code == 403

def test_get_contacts_with_valid_token(auth_headers):
    response = requests.get(f"{API_BASE_URL}/v1/contacts",headers=auth_headers)
    assert response.status_code == 200

    body = response.json()
    assert "contacts" in body
    assert isinstance(body["contacts"],list)

@pytest.mark.parametrize(
    "authorization",[
        pytest.param("Bearer asd123", id="garbage_token"),
        pytest.param("Bearer ", id="empty_token"),
        pytest.param("Basic asd123 ", id="wrong_scheme"),
    ])
def test_get_contacts_with_malformed_token_rejected(authorization):
    response = requests.get(f"{API_BASE_URL}/v1/contacts", headers={"Authorization": authorization})
    assert response.status_code == 401
    assert "message" in response.json()

#--------------------------------------------------------
def test_add_contact_success(auth_headers,contact_data):
    contact_data_dict = asdict(contact_data)
    response = requests.post(f"{API_BASE_URL}/v1/contacts",json=contact_data_dict, headers=auth_headers)
    assert response.status_code == 200
    assert "added" in response.json()["message"].lower()

    list_response = requests.get(f"{API_BASE_URL}/v1/contacts",headers=auth_headers)
    contacts = list_response.json()["contacts"]

    matching_contacts = [
        contact
        for contact in contacts
        if contact["name"] == contact_data_dict["name"]
           and contact["lastName"] == contact_data_dict["lastName"]
           and contact["email"] == contact_data_dict["email"]
           and contact["phone"] == contact_data_dict["phone"]
           and contact["address"] == contact_data_dict["address"]
    ]
    assert len(matching_contacts) > 0

def test_add_contact_success1(auth_headers,created_contact):
    payload = dict(created_contact)
    response = requests.post(f"{API_BASE_URL}/v1/contacts", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert "added" in response.json()["message"].lower()

    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    contacts = list_response.json()["contacts"]

    matching_contacts = [
        contact
        for contact in contacts
        if contact["name"] == payload["name"]
           and contact["lastName"] == payload["lastName"]
           and contact["email"] == payload["email"]
           and contact["phone"] == payload["phone"]
           and contact["address"] == payload["address"]
    ]
    assert len(matching_contacts) > 0
#--------------------------------------------------------

# def test_add_contact_success_1(auth_headers, created_contact):
#     payload = dict(created_contact)
#     response = requests.post(f"{API_BASE_URL}/v1/contacts", json=payload, headers=auth_headers)
#     contacts = response.json()["contacts"]
#
#     matching_contacts = [contact for contact in response.json()["contacts"] if contact["id"] ==created_contact["id"]]
#     assert len(matching_contacts)==1
#     assert matching_contacts[0] ==created_contact

#--------------------------------------------------------
def test_contact_full_lifecycle(auth_headers):
    contact = {
        "name": "Karina",
        "lastName": "Silvia13",
        "email": "silvia13@gmail.com",
        "phone": "050941333727854",
        "address": "Miami 27",
        "description": "Hello world!"
    }
    #CREATE
    create_response = requests.post(f"{API_BASE_URL}/v1/contacts", json=contact, headers=auth_headers)
    assert create_response.status_code == 200
    message = create_response.json()["message"]
    contact_id = message.split(": ")[1]
    print(contact_id)
#-----------------
    #READ
    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == contact_id]
    assert len(matching_contact)==1
    assert matching_contact[0]["name"] == "Karina"

    payload = dict(contact)
    payload["id"] = contact_id
    payload["name"] = "Anna-Maria"

    #UPDATE
    update_response = requests.put(f"{API_BASE_URL}/v1/contacts", json=payload, headers=auth_headers)
    assert update_response.status_code == 200
#-----------------
    #READ
    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == contact_id]
    assert len(matching_contact) == 1
    assert matching_contact[0]["name"] == "Anna-Maria"

    #DELETE
    delete_response = requests.delete(f"{API_BASE_URL}/v1/contacts/{contact_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    #READ
    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    contact_ids = [c["id"] for c in list_response.json()["contacts"]]
    assert contact_id not in contact_ids

# update contact
#     def test_update_contact_phone(auth_headers, created_contact):
#         payload = dict(created_contact)
#         payload["phone"] = "05999999999"
#
#         response = requests.put(f"{API_BASE_URL}/v1/contacts/{contact_id}", json=payload, headers=auth_headers)
#         assert delete_response.status_code == 200
#
#         list_response = requests.put(f"{API_BASE_URL}/v1/contacts/{contact_id}", json=payload, headers=auth_headers)
#         matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == contact_id]


# def test_one(auth_headers):
#     contact = Contact(
#         name = fake.first_name(),
#         lastName = fake.last_name(),
#         email = fake.email(),
#         phone = fake.numerify("05###########"),
#         address = fake.address(),
#         description = "autotest"
#     )


def test_delete_contact_success(auth_headers,created_contact):
    delete_response = requests.delete(f"{API_BASE_URL}/v1/contacts/{created_contact['id']}", headers=auth_headers)
    assert delete_response.status_code == 200

    list_response = requests.get(f"{API_BASE_URL}/v1/contacts", headers=auth_headers)
    contact_ids = [c["id"] for c in list_response.json()["contacts"]]
    assert created_contact["id"] not in contact_ids
#----------------------------------------------------------------
# @pytest.mark.parametrize("missing_field",["id","name","lastName","address"])
# def test_update_contact_with_missing_required_fields_rejected (auth_headers, created_contact,missing_field):
#     payload = dict(created_contact)
#     del payload[missing_field]
#     response = requests.post(f"{API_BASE_URL}/v1/contacts",json=payload,headers=auth_headers)
#     assert response.status_code == 400
#     assert missing_field in response.json()["message"]
#----------------------------------------------------------------
@pytest.mark.parametrize("missing_field",["name","lastName","address"])
def test_add_contact_with_missing_required_fields_rejected (auth_headers, contact_data,missing_field):
    payload = asdict(contact_data)
    del payload[missing_field]
    response = requests.post(f"{API_BASE_URL}/v1/contacts",json=payload,headers=auth_headers)
    assert response.status_code == 400
    assert missing_field in response.json()["message"]

@pytest.mark.parametrize("field, bad_value",[
    pytest.param("name", "", id = "empty name"),
    pytest.param("lastName", "", id = "empty last name"),
    pytest.param("address", "", id = "empty address"),
    pytest.param("phone", "05566", id = "phone to short"),
    pytest.param("phone", "0556677777778888888899999999", id = "phone to long"),
    pytest.param("phone", "0548889944anna", id = "phone letters"),
    pytest.param("phone", "+9720556677991", id = "phone plus"),
    pytest.param("email", "notanemail", id = "email not valid")
])
def test_add_contact_with_invalid_value_rejected(auth_headers, contact_data,field,bad_value):
    payload=asdict(contact_data)
    payload[field]=bad_value
    response = requests.post(f"{API_BASE_URL}/v1/contacts", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert field in response.json()["message"]
