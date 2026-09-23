"""
Modelo ORM de Notificación (capa de persistencia).

Cada notificación pertenece a un usuario y puede ser marcada como leída.
No se expone directamente en la API; para eso existen los schemas en
`app/schemas/notification.py`.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Anuncios/broadcasts que cualquiera puede consultar sin autenticarse.
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:  # pragma: no cover - solo utilidad de debug
        return (
            f"<Notification id={self.id} user_id={self.user_id} "
            f"is_read={self.is_read} is_public={self.is_public}>"
        )
