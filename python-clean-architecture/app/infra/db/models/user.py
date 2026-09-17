from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.infra.db.models.user_role_link import UserRoleLink

if TYPE_CHECKING:
    from app.infra.db.models.role import Role


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(primary_key=True)
    name: str
    email: str = Field(unique=True)
    password_hash: str
    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)
