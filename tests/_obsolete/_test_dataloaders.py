import sqlalchemy
import asyncio
import pytest

# from ..uoishelpers.uuid import UUIDColumn

from src.DBDefinitions import BaseModel
from src.DBDefinitions import RoleTypeModel, RoleModel
from src.DBDefinitions import UserModel, GroupModel, GroupTypeModel, MembershipModel

from tests.shared import prepare_demodata, prepare_in_memory_sqllite, get_demodata

from src.utils.Dataloaders import createLoaders


@pytest.mark.asyncio
async def test_table_users_select_a():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    loaders = createLoaders(async_session_maker)
    usersloader = loaders.users
    data = get_demodata()
    data = list(data["users"])
    userids = [u["id"] for u in data]
    awaitables = [usersloader.load(id) for id in userids]
    rows = await asyncio.gather(*awaitables)

    result = [
        {"id": u.id, "name": u.name, "surname": u.surname, "email": u.email}
        for u in rows
    ]
    for dr, rr in zip(data, result):
        assert dr == rr


from src.utils.Dataloaders import createLoaders_3


@pytest.mark.asyncio
async def test_table_users_select_b():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    loaders = createLoaders(async_session_maker)
    usersloader = loaders.users
    data = get_demodata()
    data = list(data["users"])
    userids = [u["id"] for u in data]
    awaitables = [usersloader.load(id) for id in userids]
    rows = await asyncio.gather(*awaitables)

    result = [
        {"id": u.id, "name": u.name, "surname": u.surname, "email": u.email}
        for u in rows
    ]
    for dr, rr in zip(data, result):
        assert dr == rr


from src.utils.Dataloaders import createLoaders_3


@pytest.mark.asyncio
async def test_table_users_select_c():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    loaders = createLoaders(async_session_maker)
    usersloader = loaders.users
    data = get_demodata()
    data = list(data["users"])
    userids = [u["id"] for u in data]
    awaitables = [usersloader.load(id) for id in userids]
    rows = await asyncio.gather(*awaitables)

    result = [
        {"id": u.id, "name": u.name, "surname": u.surname, "email": u.email}
        for u in rows
    ]
    for dr, rr in zip(data, result):
        assert dr == rr
