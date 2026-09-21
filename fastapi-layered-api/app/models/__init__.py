from app.models.notification import Notification  # noqa: F401 - registra el modelo en Base.metadata
from app.models.user import User  # noqa: F401 - registra el modelo en Base.metadata

__all__ = ["User", "Notification"]
