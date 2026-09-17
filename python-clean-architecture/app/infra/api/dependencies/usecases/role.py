from typing import Annotated

from fastapi import Depends

from app.core.usecases.role import (
    CreateRoleUsecase,
    DeleteRoleUsecase,
    GetRoleUsecase,
    ListRolesUsecase,
    UpdateRoleUsecase,
)
from app.core.usecases.user import AssignRoleToUserUsecase, RemoveRoleFromUserUsecase
from app.infra.api.dependencies.role import RoleRepoDep, RoleUoW, UserRoleUoW


def get_create_role_usecase(uow: RoleUoW) -> CreateRoleUsecase:
    return CreateRoleUsecase(uow)


def get_get_role_usecase(repo: RoleRepoDep) -> GetRoleUsecase:
    return GetRoleUsecase(repo)


def get_list_roles_usecase(repo: RoleRepoDep) -> ListRolesUsecase:
    return ListRolesUsecase(repo)


def get_update_role_usecase(uow: RoleUoW) -> UpdateRoleUsecase:
    return UpdateRoleUsecase(uow)


def get_delete_role_usecase(repo: RoleRepoDep) -> DeleteRoleUsecase:
    return DeleteRoleUsecase(repo)


def get_assign_role_to_user_usecase(uow: UserRoleUoW) -> AssignRoleToUserUsecase:
    return AssignRoleToUserUsecase(uow)


def get_remove_role_from_user_usecase(uow: UserRoleUoW) -> RemoveRoleFromUserUsecase:
    return RemoveRoleFromUserUsecase(uow)


CreateRole = Annotated[CreateRoleUsecase, Depends(get_create_role_usecase)]
GetRole = Annotated[GetRoleUsecase, Depends(get_get_role_usecase)]
ListRoles = Annotated[ListRolesUsecase, Depends(get_list_roles_usecase)]
UpdateRole = Annotated[UpdateRoleUsecase, Depends(get_update_role_usecase)]
DeleteRole = Annotated[DeleteRoleUsecase, Depends(get_delete_role_usecase)]
AssignRoleToUser = Annotated[AssignRoleToUserUsecase, Depends(get_assign_role_to_user_usecase)]
RemoveRoleFromUser = Annotated[RemoveRoleFromUserUsecase, Depends(get_remove_role_from_user_usecase)]
