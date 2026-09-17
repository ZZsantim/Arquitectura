from dataclasses import dataclass

from app.core.dtos.role import RoleResponse
from app.core.ports.role import RoleRepo
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class ListRolesUsecase:
    role_repo: RoleRepo

    async def execute(self) -> list[RoleResponse]:
        roles = await self.role_repo.list_all()
        logger.info("Roles listed successfully")
        return [RoleResponse(id=str(role.id), name=role.name, description=role.description) for role in roles]
