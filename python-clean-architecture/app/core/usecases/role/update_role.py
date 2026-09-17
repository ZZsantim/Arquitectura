from dataclasses import dataclass

from app.core.dtos.role import RoleResponse, UpdateRole
from app.core.entities.role import Role
from app.core.exceptions import RoleNotFoundError
from app.core.ports.role import RoleUnitOfWork
from app.core.value_objects.id import ID
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class UpdateRoleUsecase:
    uow: RoleUnitOfWork

    async def execute(self, role_id: str, dto: UpdateRole) -> RoleResponse:
        id_value = ID.from_string(role_id)

        async with self.uow:
            existing_role = await self.uow.role_repo.get_by_id(id_value)
            if not existing_role:
                raise RoleNotFoundError(f"Role with ID {role_id} not found")

            updated_role = await self.uow.role_repo.update(
                Role(
                    id=existing_role.id,
                    name=(dto.name or existing_role.name).strip(),
                    description=dto.description if dto.description is not None else existing_role.description,
                )
            )

            if not updated_role:
                raise RoleNotFoundError(f"Role with ID {role_id} not found")

            logger.info(f"Role {role_id} updated successfully")
            return RoleResponse(
                id=str(updated_role.id),
                name=updated_role.name,
                description=updated_role.description,
            )
