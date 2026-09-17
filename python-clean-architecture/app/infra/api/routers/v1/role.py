from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.dtos.role import CreateRoleRequest, RoleResponse, UpdateRole
from app.core.exceptions import InvalidRoleError, RoleAlreadyExistsError, RoleNotFoundError
from app.core.value_objects.id import InvalidIDError
from app.infra.api.dependencies.usecases.role import (
    CreateRole as CreateRoleUsecase,
    DeleteRole as DeleteRoleUsecase,
    GetRole as GetRoleUsecase,
    ListRoles as ListRolesUsecase,
    UpdateRole as UpdateRoleUsecase,
)

router = APIRouter()


@router.post(
    "",
    status_code=201,
    summary="Creates new Role",
    responses={
        201: {"description": "Role created successfully"},
        400: {"description": "Invalid role data"},
        409: {"description": "Role already exists"},
    },
)
async def create(dto: CreateRoleRequest, usecase: CreateRoleUsecase) -> RoleResponse:
    try:
        return await usecase.execute(dto)
    except InvalidRoleError as e:
        raise HTTPException(400, detail=str(e))
    except RoleAlreadyExistsError:
        raise HTTPException(409, detail="Role already exists")


@router.get(
    "",
    summary="Lists roles",
    responses={200: {"description": "Roles found"}},
)
async def list_roles(usecase: ListRolesUsecase) -> list[RoleResponse]:
    return await usecase.execute()


@router.get(
    "/{role_id}",
    summary="Gets Role information",
    responses={
        200: {"description": "Role found"},
        404: {"description": "Role not found"},
    },
)
async def get(role_id: UUID, usecase: GetRoleUsecase) -> RoleResponse:
    try:
        return await usecase.execute(str(role_id))
    except InvalidIDError as e:
        raise HTTPException(status_code=422, detail=f"Invalid role ID: {e}")
    except RoleNotFoundError:
        raise HTTPException(status_code=404, detail="Role not found")


@router.patch(
    "/{role_id}",
    summary="Updates Role information",
    responses={
        200: {"description": "Role updated"},
        400: {"description": "Invalid role data"},
        404: {"description": "Role not found"},
    },
)
async def patch(role_id: UUID, dto: UpdateRole, usecase: UpdateRoleUsecase) -> RoleResponse:
    try:
        return await usecase.execute(str(role_id), dto)
    except RoleNotFoundError:
        raise HTTPException(status_code=404, detail="Role not found")
    except InvalidRoleError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{role_id}",
    status_code=204,
    summary="Deletes Role",
    responses={
        204: {"description": "Role deleted successfully"},
        404: {"description": "Role not found"},
    },
)
async def delete(role_id: UUID, usecase: DeleteRoleUsecase) -> None:
    if not await usecase.execute(str(role_id)):
        raise HTTPException(status_code=404, detail="Role not found")
