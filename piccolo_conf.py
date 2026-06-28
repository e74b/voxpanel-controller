from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine
from config import POSTGRES_URL

URL = POSTGRES_URL 
DB = PostgresEngine(config={"dsn": URL})


# A list of paths to piccolo apps
# e.g. ['blog.piccolo_app']
APP_REGISTRY = AppRegistry(
    apps=["auth.piccolo_app", "server.piccolo_app", "agents.piccolo_app"]
)
