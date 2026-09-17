from app.core.ports.role import RoleUnitOfWork
from app.infra.db import DBSession
from app.infra.db.repositories.role import RoleRepo
from app.infra.db.repositories.user import UserRepo
from app.infra.db.repositories.user_role import UserRoleRepo
from app.infra.db.unit_of_work.base import BaseUnitOfWork


class UserRoleUnitOfWork(BaseUnitOfWork):
    def __init__(self, session: DBSession) -> None:
        super().__init__(session)
        self.user_repo = UserRepo(session)
        self.role_repo = RoleRepo(session)
        self.user_role_repo = UserRoleRepo(session)


def user_role_uow_factory(session: DBSession) -> UserRoleUnitOfWork:
    return UserRoleUnitOfWork(session)
