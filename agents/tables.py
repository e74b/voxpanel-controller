from piccolo.table import Table
from piccolo.columns import Varchar, Timestamptz


class Agent(Table):
    agent_name = Varchar()
    token = Varchar()
    last_ping = Timestamptz(default=None, null=True)
