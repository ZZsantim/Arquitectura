from dataclasses import dataclass

from app.core.dtos.role import RoleResponse
from app.core.exceptions import RoleNotFoundError
from app.core.ports.role import RoleRepo
from app.core.value_objects.id import ID
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class GetRoleUsecase:
    role_repo: RoleRepo

    async def execute(self, role_id: str) -> RoleResponse:
        id_value = ID.from_string(role_id)
        role = await self.role_repo.get_by_id(id_value)
        if not role:
            raise RoleNotFoundError(f"Role with ID {role_id} not found")

        logger.info(f"Role {role_id} retrieved successfully")
        return RoleResponse(id=str(role.id), name=role.name, description=role.description)
