from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.infra.db.models.user_role_link import UserRoleLink

if TYPE_CHECKING:
    from app.infra.db.models.user import User


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: UUID = Field(primary_key=True)
    name: str = Field(unique=True)
    description: str = ""
    users: list["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)
