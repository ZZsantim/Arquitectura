"""
Repositorio de Notificación (patrón Repository).

Responsabilidad única: encapsular consultas SQLAlchemy relacionadas con
notificaciones. No conoce reglas de negocio ni HTTP.
"""

from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, user_id: int, message: str) -> Notification:
        notification = Notification(user_id=user_id, message=message)
        self._session.add(notification)
        await self._session.flush()
        await self._session.refresh(notification)
        return notification

    async def get_by_id_for_user(self, notification_id: int, user_id: int) -> Optional[Notification]:
        result = await self._session.execute(
            select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: int,
        *,
        offset: int = 0,
        limit: int = 20,
        is_read: Optional[bool] = None,
    ) -> tuple[Sequence[Notification], int]:
        query = select(Notification).where(Notification.user_id == user_id)
        if is_read is not None:
            query = query.where(Notification.is_read.is_(is_read))
        query = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)

        total_query = select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
        if is_read is not None:
            total_query = total_query.where(Notification.is_read.is_(is_read))

        items_result = await self._session.execute(query)
        total_result = await self._session.execute(total_query)
        return items_result.scalars().all(), total_result.scalar_one()

    async def mark_as_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        await self._session.flush()
        await self._session.refresh(notification)
        return notification

    async def delete(self, notification: Notification) -> None:
        await self._session.delete(notification)
        await self._session.flush()
