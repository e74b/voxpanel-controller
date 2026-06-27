from piccolo.table import Table
from piccolo.columns import Varchar, Text, ForeignKey, UUID
from auth.tables import User


class Server(Table):
    slug = Varchar(unique=True)
    uuid = UUID()
    owner = ForeignKey(User)
    state = Varchar(default="offline")
    run_id = Varchar(null=True, default=None)
