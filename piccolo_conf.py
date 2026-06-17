from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine


URL = "postgresql://default:password@127.0.0.1:5432/voxpanel"
DB = PostgresEngine(config={
    "dsn": URL
    })


# A list of paths to piccolo apps
# e.g. ['blog.piccolo_app']
APP_REGISTRY = AppRegistry(apps=[
    "auth.piccolo_app",
    "server.piccolo_app"
    ])
