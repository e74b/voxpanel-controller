from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod

ID = "2026-06-22T11:40:12:594951"
VERSION = "1.34.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="agents", description=DESCRIPTION
    )

    manager.add_table(class_name="Agent", tablename="agent", schema=None, columns=None)

    manager.add_column(
        table_class_name="Agent",
        tablename="agent",
        column_name="agent_name",
        db_column_name="agent_name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "",
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

    manager.add_column(
        table_class_name="Agent",
        tablename="agent",
        column_name="token",
        db_column_name="token",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "",
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

    manager.add_column(
        table_class_name="Agent",
        tablename="agent",
        column_name="last_ping",
        db_column_name="last_ping",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": None,
            "null": True,
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
