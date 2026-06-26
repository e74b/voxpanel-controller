from auth import User, Scope, Permission 
import asyncio

async def setup_users_main():
    u = User(username="admin", password="default")
    await User.insert(u)

    admin_scope = Scope(user=u, scope=Permission.ADMIN)
    await Scope.insert(admin_scope)

asyncio.run(setup_users_main())
