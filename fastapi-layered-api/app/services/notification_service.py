"""Servicio de Notificación (capa de lógica de negocio)."""

from app.core.exceptions import NotificationNotFoundError
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationCreate


class NotificationService:
    def __init__(self, repository: NotificationRepository) -> None:
        self._repository = repository

    async def create_notification(self, user_id: int, data: NotificationCreate):
        return await self._repository.create(user_id=user_id, message=data.message)

    async def list_notifications(self, user_id: int, *, page: int, page_size: int, is_read=None):
        offset = (page - 1) * page_size
        notifications, total = await self._repository.list_for_user(
            user_id,
            offset=offset,
            limit=page_size,
            is_read=is_read,
        )
        return list(notifications), total

    async def list_public_announcements(self, *, page: int, page_size: int):
        """Consulta pública sin identificador de usuario."""
        offset = (page - 1) * page_size
        notifications, total = await self._repository.list_public(
            offset=offset,
            limit=page_size,
        )
        return list(notifications), total

    async def mark_as_read(self, notification_id: int, user_id: int):
        notification = await self._repository.get_by_id_for_user(notification_id, user_id)
        if notification is None:
            raise NotificationNotFoundError(
                f"Notificación con id={notification_id} no encontrada o no pertenece al usuario."
            )
        return await self._repository.mark_as_read(notification)

    async def delete_notification(self, notification_id: int, user_id: int) -> None:
        notification = await self._repository.get_by_id_for_user(notification_id, user_id)
        if notification is None:
            raise NotificationNotFoundError(
                f"Notificación con id={notification_id} no encontrada o no pertenece al usuario."
            )
        await self._repository.delete(notification)
