import sqlalchemy
import asyncio
import pytest

# from ..uoishelpers.uuid import UUIDColumn

from src.DBDefinitions import BaseModel
from src.DBDefinitions import RoleTypeModel, RoleModel
from src.DBDefinitions import UserModel, GroupModel, GroupTypeModel, MembershipModel

from tests.shared import prepare_demodata, prepare_in_memory_sqllite, get_demodata


# @pytest.mark.asyncio
# async def _test_load_system_data():
#     async_session_maker = await prepare_in_memory_sqllite()
#     await predefineAllDataStructures(async_session_maker)


# @pytest.mark.asyncio
# async def _test_random_data():
#     async_session_maker = await prepare_in_memory_sqllite()
#     await predefineAllDataStructures(async_session_maker)
#     async with async_session_maker() as session:
#         await randomDataStructure(session, "")


# from src.DBFeeder import (
#     createSystemDataStructureRoleTypes,
#     createSystemDataStructureGroupTypes,
# )


# @pytest.mark.asyncio
# async def _test_system_data():
#     async_session_maker = await prepare_in_memory_sqllite()
#     await predefineAllDataStructures(async_session_maker)
#     await createSystemDataStructureRoleTypes(async_session_maker)
#     await createSystemDataStructureGroupTypes(async_session_maker)

#     # duplicit for errors
#     await createSystemDataStructureRoleTypes(async_session_maker)
#     await createSystemDataStructureGroupTypes(async_session_maker)
