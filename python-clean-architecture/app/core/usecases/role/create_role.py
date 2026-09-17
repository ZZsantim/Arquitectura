from dataclasses import dataclass

from app.core.dtos.role import CreateRoleRequest, RoleResponse
from app.core.entities.role import Role
from app.core.exceptions import RoleAlreadyExistsError
from app.core.ports.role import RoleUnitOfWork
from app.core.value_objects.id import ID
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class CreateRoleUsecase:
    uow: RoleUnitOfWork

    async def execute(self, dto: CreateRoleRequest) -> RoleResponse:
        name = dto.name.strip()
        role = Role(id=ID.generate(), name=name, description=dto.description or "")

        async with self.uow:
            if await self.uow.role_repo.get_by_name(name):
                logger.warning(f"Role with name {name} already exists")
                raise RoleAlreadyExistsError(f"Role with name {name} already exists")

            await self.uow.role_repo.save(role)
            logger.info(f"Role {role.name} created successfully")
            return RoleResponse(id=str(role.id), name=role.name, description=role.description)
