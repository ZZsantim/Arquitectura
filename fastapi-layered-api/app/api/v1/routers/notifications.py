"""Router: Notificaciones públicas y privadas del usuario autenticado."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_active_user, get_notification_service
from app.core.exceptions import NotificationNotFoundError
from app.models.user import User
from app.schemas.common import ErrorResponse
from app.schemas.notification import (
    NotificationAnnouncementListResponse,
    NotificationCreate,
    NotificationListResponse,
    NotificationPublic,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get(
    "/public",
    response_model=NotificationAnnouncementListResponse,
    summary="Consultar anuncios públicos (sin autenticación)",
)
async def list_public_announcements(
    service: Annotated[NotificationService, Depends(get_notification_service)],
    page: Annotated[int, Query(ge=1, description="Número de página (1-indexado)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Tamaño de página (máx. 100)")] = 20,
) -> NotificationAnnouncementListResponse:
    """Devuelve solo anuncios generales marcados como públicos."""
    notifications, total = await service.list_public_announcements(
        page=page,
        page_size=page_size,
    )
    return NotificationAnnouncementListResponse(
        items=notifications,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=NotificationPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una notificación para el usuario autenticado",
)
async def create_notification(
    payload: NotificationCreate,
    service: Annotated[NotificationService, Depends(get_notification_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> NotificationPublic:
    notification = await service.create_notification(current_user.id, payload)
    return NotificationPublic.model_validate(notification)


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="Listar notificaciones del usuario autenticado",
)
async def list_notifications(
    service: Annotated[NotificationService, Depends(get_notification_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: Annotated[int, Query(ge=1, description="Número de página (1-indexado)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Tamaño de página (máx. 100)")] = 20,
    is_read: Optional[bool] = Query(None, description="Filtrar por estado de lectura"),
) -> NotificationListResponse:
    notifications, total = await service.list_notifications(
        current_user.id,
        page=page,
        page_size=page_size,
        is_read=is_read,
    )
    return NotificationListResponse(
        items=[NotificationPublic.model_validate(n) for n in notifications],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationPublic,
    summary="Marcar una notificación como leída",
    responses={404: {"model": ErrorResponse}},
)
async def mark_notification_as_read(
    notification_id: int,
    service: Annotated[NotificationService, Depends(get_notification_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> NotificationPublic:
    try:
        notification = await service.mark_as_read(notification_id, current_user.id)
    except NotificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return NotificationPublic.model_validate(notification)


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una notificación",
    responses={404: {"model": ErrorResponse}},
)
async def delete_notification(
    notification_id: int,
    service: Annotated[NotificationService, Depends(get_notification_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    try:
        await service.delete_notification(notification_id, current_user.id)
    except NotificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
