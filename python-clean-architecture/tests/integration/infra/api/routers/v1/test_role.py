from uuid import uuid4

import pytest


@pytest.fixture
def role_route():
    return "/api/v1/roles"


@pytest.fixture
def user_route():
    return "/api/v1/users"


@pytest.fixture
def role_payload():
    return {"name": "admin", "description": "Administrator access"}


@pytest.fixture
def user_payload():
    return {"name": "Alice", "email": "alice@example.com", "password": "password"}


async def test_create_role_persistence(client, role_route, role_payload):
    response = await client.post(role_route, json=role_payload)
    data, status_code = response.json(), response.status_code

    assert status_code == 201
    assert data["name"] == role_payload["name"]
    assert data["description"] == role_payload["description"]

    get_response = await client.get(f"{role_route}/{data['id']}")
    fetched, fetched_status = get_response.json(), get_response.status_code

    assert fetched_status == 200
    assert fetched["id"] == data["id"]
    assert fetched["name"] == role_payload["name"]


async def test_create_role_conflict(client, role_route, role_payload):
    await client.post(role_route, json=role_payload)
    response = await client.post(role_route, json=role_payload)
    data, status_code = response.json(), response.status_code

    assert status_code == 409
    assert data == {"detail": "Role already exists"}


async def test_assign_role_to_user_and_list_roles(client, role_route, user_route, role_payload, user_payload):
    user_response = await client.post(user_route, json=user_payload)
    user_id = user_response.json()["id"]

    role_response = await client.post(role_route, json=role_payload)
    role_id = role_response.json()["id"]

    assign_response = await client.post(f"{user_route}/{user_id}/roles/{role_id}")
    assert assign_response.status_code == 204

    get_user_response = await client.get(f"{user_route}/{user_id}")
    assert get_user_response.status_code == 200
    assert get_user_response.json()["roles"] == [role_payload["name"]]

    list_roles_response = await client.get(f"{user_route}/{user_id}/roles")
    assert list_roles_response.status_code == 200
    assert list_roles_response.json() == [role_payload["name"]]

    remove_response = await client.delete(f"{user_route}/{user_id}/roles/{role_id}")
    assert remove_response.status_code == 204

    refreshed_user = await client.get(f"{user_route}/{user_id}")
    assert refreshed_user.status_code == 200
    assert refreshed_user.json()["roles"] == []


async def test_get_role_not_found(client, role_route):
    response = await client.get(f"{role_route}/{uuid4()}")
    data, status_code = response.json(), response.status_code

    assert status_code == 404
    assert data == {"detail": "Role not found"}
