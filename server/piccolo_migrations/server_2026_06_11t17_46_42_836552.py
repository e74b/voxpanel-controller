from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar

ID = "2026-06-11T17:46:42:836552"
VERSION = "1.34.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="server", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="Server",
        tablename="server",
        column_name="slug",
        db_column_name="slug",
        params={"unique": True},
        old_params={"unique": False},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    return manager
