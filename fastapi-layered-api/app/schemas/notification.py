"""Schemas (contratos de la API) para el recurso Notificación."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="Texto de la notificación.")


class NotificationPublic(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    is_public: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    items: list[NotificationPublic]
    total: int
    page: int
    page_size: int


class NotificationAnnouncement(BaseModel):
    """Vista reducida para anuncios consultables sin autenticación."""

    id: int
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationAnnouncementListResponse(BaseModel):
    items: list[NotificationAnnouncement]
    total: int
    page: int
    page_size: int
