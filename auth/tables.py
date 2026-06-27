from piccolo.table import Table
from piccolo.columns import Varchar, Text, ForeignKey


class User(Table, tablename="users"):
    username = Varchar(unique=True)
    password = Text()


class Scope(Table):
    user = ForeignKey(references=User)
    scope = Varchar(length=512)
