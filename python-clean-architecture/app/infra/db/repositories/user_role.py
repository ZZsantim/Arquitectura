from sqlmodel import select

from app.core.entities.role import Role
from app.core.value_objects.id import ID
from app.infra.db import DBSession
from app.infra.db.models.role import Role as DBRole
from app.infra.db.models.user_role_link import UserRoleLink


class UserRoleRepo:
    def __init__(self, session: DBSession) -> None:
        self.session = session

    async def assign_role(self, user_id: ID, role_id: ID) -> None:
        self.session.add(UserRoleLink(user_id=user_id.value, role_id=role_id.value))

    async def remove_role(self, user_id: ID, role_id: ID) -> None:
        row = await self.session.get(UserRoleLink, {"user_id": user_id.value, "role_id": role_id.value})
        if row is not None:
            await self.session.delete(row)

    async def list_roles(self, user_id: ID) -> list[Role]:
        result = await self.session.exec(
            select(DBRole).join(UserRoleLink, UserRoleLink.role_id == DBRole.id).where(UserRoleLink.user_id == user_id.value)
        )
        roles = result.all()
        return [
            Role(id=ID.from_string(str(role.id)), name=role.name, description=role.description)
            for role in roles
        ]
