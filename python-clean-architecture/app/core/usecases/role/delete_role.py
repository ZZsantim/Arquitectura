from dataclasses import dataclass

from app.core.ports.role import RoleRepo
from app.core.value_objects.id import ID
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class DeleteRoleUsecase:
    role_repo: RoleRepo

    async def execute(self, role_id: str) -> bool:
        id_value = ID.from_string(role_id)
        result = await self.role_repo.delete(id_value)
        if result:
            logger.info(f"Role {role_id} deleted successfully")
        return result
