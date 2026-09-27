"""Add name column to users table

Revision ID: 6d62029bb66e
Revises: 001_initial_migration
Create Date: 2025-07-26 01:20:41.091056

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "6d62029bb66e"
down_revision = "001_initial_migration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # NOTA (compatibilidad Python 3.14 / SQLite local): SQLite no soporta
    # ALTER COLUMN ni DROP COLUMN directos como Postgres. Se envuelven los
    # mismos cambios en op.batch_alter_table, que sigue funcionando igual
    # en Postgres y además funciona en SQLite (recrea la tabla por debajo).
    # Antes estaba así (comentado, no se borró nada):
    # op.add_column(
    #     "users",
    #     sa.Column(
    #         "name", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=""
    #     ),
    # )
    # op.alter_column("users", "name", server_default=None)
    # op.drop_column("users", "created_at")
    # op.drop_column("users", "updated_at")
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column(
                "name", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=""
            ),
        )
        batch_op.alter_column("name", server_default=None)
        batch_op.drop_column("created_at")
        batch_op.drop_column("updated_at")


def downgrade() -> None:
    # Antes estaba así (comentado, no se borró nada):
    # op.add_column(
    #     "users",
    #     sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    # )
    # op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))
    # op.drop_column("users", "name")
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=True))
        batch_op.drop_column("name")
