from typing import Optional

from sqlmodel import select

from app.core.entities.role import Role
from app.core.value_objects.id import ID
from app.infra.db import DBSession
from app.infra.db.models.role import Role as DBRole


class RoleRepo:
    def __init__(self, session: DBSession) -> None:
        self.session = session

    async def save(self, role: Role) -> None:
        db_role = DBRole(id=role.id.value, name=role.name, description=role.description)
        self.session.add(db_role)

    async def get_by_id(self, _id: ID) -> Optional[Role]:
        db_role = await self.session.get(DBRole, _id.value)
        if not db_role:
            return None
        return Role(id=ID.from_string(str(db_role.id)), name=db_role.name, description=db_role.description)

    async def get_by_name(self, name: str) -> Optional[Role]:
        result = await self.session.exec(select(DBRole).where(DBRole.name == name))
        db_role = result.first()
        if not db_role:
            return None
        return Role(id=ID.from_string(str(db_role.id)), name=db_role.name, description=db_role.description)

    async def list_all(self) -> list[Role]:
        result = await self.session.exec(select(DBRole))
        roles = result.all()
        return [
            Role(id=ID.from_string(str(role.id)), name=role.name, description=role.description)
            for role in roles
        ]

    async def delete(self, _id: ID) -> bool:
        db_role = await self.session.get(DBRole, _id.value)
        if not db_role:
            return False
        await self.session.delete(db_role)
        return True

    async def update(self, role: Role) -> Optional[Role]:
        to_update = await self.session.get(DBRole, role.id.value)
        if not to_update:
            return None

        to_update.name = role.name
        to_update.description = role.description
        self.session.add(to_update)
        return role
