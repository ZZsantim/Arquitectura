from typing import Annotated, AsyncGenerator

from fastapi import Depends

from app.core.ports.role import RoleUnitOfWork
from app.infra.db import async_session
from app.infra.db.repositories.role import RoleRepo
from app.infra.db.unit_of_work.role import user_role_uow_factory


async def get_role_repo() -> AsyncGenerator[RoleRepo, None]:
    async with async_session() as session:
        yield RoleRepo(session)


async def get_role_uow() -> AsyncGenerator[RoleUnitOfWork, None]:
    async with async_session() as session:
        yield user_role_uow_factory(session)  # type: ignore[misc]


RoleRepoDep = Annotated[RoleRepo, Depends(get_role_repo)]
RoleUoW = Annotated[RoleUnitOfWork, Depends(get_role_uow)]
UserRoleUoW = RoleUoW
