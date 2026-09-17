from dataclasses import dataclass

from app.core.exceptions import RoleNotFoundError, UserNotFoundError
from app.core.ports.user import UserRoleUnitOfWork
from app.core.value_objects.id import ID
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class AssignRoleToUserUsecase:
    uow: UserRoleUnitOfWork

    async def execute(self, user_id: str, role_id: str) -> None:
        user_id_value = ID.from_string(user_id)
        role_id_value = ID.from_string(role_id)

        async with self.uow:
            user = await self.uow.user_repo.get_by_id(user_id_value)
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            role = await self.uow.role_repo.get_by_id(role_id_value)
            if not role:
                raise RoleNotFoundError(f"Role with ID {role_id} not found")

            await self.uow.user_role_repo.assign_role(user_id_value, role_id_value)
            logger.info(f"Role {role_id} assigned to user {user_id}")
