from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod

ID = "2026-06-11T10:03:36:951296"
VERSION = "1.34.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="server", description=DESCRIPTION
    )

    manager.add_column(
        table_class_name="Server",
        tablename="server",
        column_name="state",
        db_column_name="state",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "offline",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager
