"""Tests para el recurso Notification."""

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def test_post_notification_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/api/v1/notifications", json={"message": "Hola"})
    assert response.status_code == 401


async def test_public_announcements_do_not_require_auth(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    announcement = Notification(
        user_id=1,
        message="Mantenimiento programado",
        is_public=True,
    )
    private = Notification(
        user_id=1,
        message="Notificación privada",
        is_public=False,
    )
    db_session.add_all([announcement, private])
    await db_session.flush()

    response = await client.get("/api/v1/notifications/public")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["message"] == "Mantenimiento programado"
    assert "user_id" not in body["items"][0]


async def test_create_and_list_notification(client: AsyncClient, user_payload: dict) -> None:
    register_response = await client.post("/api/v1/auth/register", json=user_payload)
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/api/v1/notifications",
        json={"message": "Recordatorio de pago"},
        headers=headers,
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["message"] == "Recordatorio de pago"
    assert created["is_read"] is False

    list_response = await client.get("/api/v1/notifications", headers=headers)
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["message"] == "Recordatorio de pago"


async def test_mark_notification_as_read(client: AsyncClient, user_payload: dict) -> None:
    register_response = await client.post("/api/v1/auth/register", json=user_payload)
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/api/v1/notifications",
        json={"message": "Tu compra fue confirmada"},
        headers=headers,
    )
    assert create_response.status_code == 201
    notification_id = create_response.json()["id"]

    patch_response = await client.patch(
        f"/api/v1/notifications/{notification_id}/read",
        headers=headers,
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["is_read"] is True


async def test_second_user_cannot_mark_other_users_notification(client: AsyncClient, user_payload: dict) -> None:
    first_payload = user_payload
    second_payload = {
        "email": "grace.hopper@example.com",
        "full_name": "Grace Hopper",
        "password": "SuperSecreta456",
    }

    first_register = await client.post("/api/v1/auth/register", json=first_payload)
    assert first_register.status_code == 201
    second_register = await client.post("/api/v1/auth/register", json=second_payload)
    assert second_register.status_code == 201

    first_login = await client.post(
        "/api/v1/auth/login",
        data={"username": first_payload["email"], "password": first_payload["password"]},
    )
    assert first_login.status_code == 200
    first_token = first_login.json()["access_token"]
    first_headers = {"Authorization": f"Bearer {first_token}"}

    create_response = await client.post(
        "/api/v1/notifications",
        json={"message": "Notificación privada"},
        headers=first_headers,
    )
    assert create_response.status_code == 201
    notification_id = create_response.json()["id"]

    second_login = await client.post(
        "/api/v1/auth/login",
        data={"username": second_payload["email"], "password": second_payload["password"]},
    )
    assert second_login.status_code == 200
    second_token = second_login.json()["access_token"]
    second_headers = {"Authorization": f"Bearer {second_token}"}

    patch_response = await client.patch(
        f"/api/v1/notifications/{notification_id}/read",
        headers=second_headers,
    )
    assert patch_response.status_code == 404


async def test_delete_notification_and_list_is_empty(client: AsyncClient, user_payload: dict) -> None:
    register_response = await client.post("/api/v1/auth/register", json=user_payload)
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/api/v1/notifications",
        json={"message": "Mensaje para borrar"},
        headers=headers,
    )
    assert create_response.status_code == 201
    notification_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/notifications/{notification_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    list_response = await client.get("/api/v1/notifications", headers=headers)
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] == 0
    assert len(body["items"]) == 0
