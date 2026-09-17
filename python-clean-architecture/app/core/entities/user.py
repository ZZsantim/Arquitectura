from dataclasses import dataclass, field

from app.core.entities.role import Role
from app.core.exceptions import InvalidUserError
from app.core.value_objects.email import Email
from app.core.value_objects.id import ID
from app.core.value_objects.password import Password


@dataclass(frozen=True, kw_only=True)
class User:
    id: ID
    name: str
    email: Email
    password: Password
    roles: tuple[Role, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise InvalidUserError("Name cannot be empty")
