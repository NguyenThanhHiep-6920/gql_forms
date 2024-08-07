import sqlalchemy
import asyncio
import pytest
import logging
import uuid
import os

os.environ.setdefault("DEMO", "True")

# from ..uoishelpers.uuid import UUIDColumn
from src.GraphTypeDefinitions import schema

from src.DBDefinitions import BaseModel
from src.DBDefinitions import RoleTypeModel, RoleModel, RoleCategoryModel
from src.DBDefinitions import UserModel, GroupModel, GroupTypeModel, MembershipModel


async def prepare_in_memory_sqllite():
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    asyncEngine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # asyncEngine = create_async_engine("sqlite+aiosqlite:///data.sqlite")
    async with asyncEngine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    async_session_maker = sessionmaker(
        asyncEngine, expire_on_commit=False, class_=AsyncSession
    )

    return async_session_maker

from src.DBFeeder import get_demodata

async def prepare_demodata(async_session_maker):
    data = get_demodata()

    from uoishelpers.feeders import ImportModels

    await ImportModels(
        async_session_maker,
        [
            UserModel,
            GroupModel,
            GroupTypeModel,
            MembershipModel,
            RoleCategoryModel,
            RoleTypeModel,
            RoleModel,
        ],
        data,
    )


from src.utils.Dataloaders import createLoaders_3, createLoaders


def createContext(asyncSessionMaker):
    return {
        "asyncSessionMaker": asyncSessionMaker,
        "all": createLoaders(asyncSessionMaker),
        "loaders": createLoaders(asyncSessionMaker),
    }


useID = False
def changeGQLQuery(GQLQuery):
    if useID:
        return GQLQuery.replace("UUID", "ID")
    else:
        return GQLQuery

def changeVariables(variables):
    if not useID:
        return variables
    result = {}
    for key, value in variables.items():
        if isinstance(value, uuid.UUID):
            result[key] = f'{value}'
        else:
            result[key] = value
    return result

def CreateSchemaFunction():
    async def result(query, variables={}):

        async_session_maker = await prepare_in_memory_sqllite()
        await prepare_demodata(async_session_maker)
        context_value = createContext(async_session_maker)
        query = changeGQLQuery(query)
        variables = changeVariables(variables)
        logging.debug(f"query for {query} with {variables}")
        print(f"query for {query} with {variables}")
        resp = await schema.execute(
            query=query, 
            variable_values=variables, 
            context_value=context_value
        )

        assert resp.errors is None
        respdata = resp.data
        logging.debug(f"response: {respdata}")

        result = {"data": respdata, "errors": resp.errors}
        return result

    return result