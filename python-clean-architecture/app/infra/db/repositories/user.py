from typing import Optional

from sqlmodel import select

from app.core.entities.role import Role
from app.core.entities.user import User
from app.core.value_objects.email import Email
from app.core.value_objects.id import ID
from app.core.value_objects.password import Password
from app.infra.db import DBSession
from app.infra.db.models.role import Role as DBRole
from app.infra.db.models.user import User as DBUser
from app.infra.db.models.user_role_link import UserRoleLink


class UserRepo:
    def __init__(self, session: DBSession) -> None:
        self.session = session

    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email address."""
        result = await self.session.exec(select(DBUser).where(DBUser.email == email.value))
        db_user = result.first()
        if not db_user:
            return None

        return await self._to_entity(db_user)

    async def save(self, user: User) -> None:
        """Save user (for backward compatibility)."""
        db_user = DBUser(
            id=user.id.value,
            name=user.name,
            email=user.email.value,
            password_hash=user.password.value,
        )
        self.session.add(db_user)

    async def get_by_id(self, _id: ID) -> Optional[User]:
        """Get user by ID."""
        db_user = await self.session.get(DBUser, _id.value)
        if not db_user:
            return None

        return await self._to_entity(db_user)

    async def delete(self, _id: ID) -> bool:
        """Delete user by ID."""
        db_user = await self.session.get(DBUser, _id.value)
        if not db_user:
            return False
        await self.session.delete(db_user)
        return True

    async def update(self, user: User) -> Optional[User]:
        """Update existing user."""
        to_update = await self.session.get(DBUser, user.id.value)
        if not to_update:
            return None

        to_update.name = user.name
        to_update.email = user.email.value
        to_update.password_hash = user.password.value
        self.session.add(to_update)
        return user

    async def _get_roles_for_user(self, user_id) -> tuple[Role, ...]:
        result = await self.session.exec(
            select(DBRole)
            .join(UserRoleLink, UserRoleLink.role_id == DBRole.id)
            .where(UserRoleLink.user_id == user_id)
        )
        roles = result.all()
        return tuple(
            Role(id=ID.from_string(str(role.id)), name=role.name, description=role.description)
            for role in roles
        )

    async def _to_entity(self, db_user: DBUser) -> User:
        roles = await self._get_roles_for_user(db_user.id)
        return User(
            id=ID.from_string(str(db_user.id)),
            name=db_user.name,
            email=Email(db_user.email),
            password=Password(db_user.password_hash),
            roles=roles,
        )
