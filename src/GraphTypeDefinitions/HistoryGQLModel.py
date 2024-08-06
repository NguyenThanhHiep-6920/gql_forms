import strawberry
import datetime
import typing
import uuid

from typing import Annotated

from uoishelpers.resolvers import getLoadersFromInfo, getUserFromInfo

from .BaseGQLModel import BaseGQLModel
from ._GraphPermissions import RoleBasedPermission, OnlyForAuthentized
from ._GraphResolvers import (
    resolve_id,
    resolve_name,
    resolve_name_en,
    resolve_changedby,
    resolve_created,
    resolve_lastchange,
    resolve_createdby,
    resolve_rbacobject,
    # createRootResolver_by_id,
    # createRootResolver_by_page
)

FormGQLModel = Annotated["FormGQLModel", strawberry.lazy(".FormGQLModel")]
RequestGQLModel = Annotated["RequestGQLModel", strawberry.lazy(".RequestGQLModel")]
StateGQLModel = Annotated["StateGQLModel", strawberry.lazy(".externals")]

@strawberry.federation.type(
    keys=["id"], 
    name="RequestHistoryGQLModel",
    description="""Entity which stores a history of form evolution during a request. This allows to recall form changes."""
)
class HistoryGQLModel(BaseGQLModel):
    """
    Type representing a request in the system.
    This class extends the base `RequestModel` from the database and adds additional fields and methods needed for use in GraphQL.
    """
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).histories
    
    # @classmethod
    # async def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID):
    # implementation is inherited

    id = resolve_id
    name = resolve_name
    changedby = resolve_changedby
    lastchange = resolve_lastchange
    created = resolve_created
    createdby = resolve_createdby
    name_en = resolve_name_en
    rbacobject = resolve_rbacobject

    @strawberry.field(
        description="""Request which history belongs to""",
        permission_classes=[OnlyForAuthentized])
    async def request(self, info: strawberry.types.Info) -> typing.Optional["RequestGQLModel"]:
        from .RequestGQLModel import RequestGQLModel
        result = await RequestGQLModel.resolve_reference(info, self.request_id)
        return result

    @strawberry.field(
        description="""History form""",
        permission_classes=[OnlyForAuthentized])
    async def form(self, info: strawberry.types.Info) -> typing.Optional["FormGQLModel"]:
        from .FormGQLModel import FormGQLModel
        result = await FormGQLModel.resolve_reference(info, self.form_id)
        return result
    
    @strawberry.field(
        description="State od the form",
        permission_classes=[OnlyForAuthentized])
    async def state(self, info: strawberry.types.Info) -> typing.Optional["StateGQLModel"]:
        #user = UserGQLModel(id=self.createdby)
        from .externals import StateGQLModel
        return await StateGQLModel.resolve_reference(info=info, id=self.state_id)

#############################################################
#
# Queries
#
#############################################################
@strawberry.field(
    description="returns the history result by its id",
    permission_classes=[OnlyForAuthentized])
async def form_history_by_id(self, info: strawberry.types.Info, id: uuid.UUID) -> typing.Optional[HistoryGQLModel]:
    return await HistoryGQLModel.resolve_reference(info=info, id=id)
#############################################################
#
# Mutations
#
#############################################################


@strawberry.input(description="Input structure - C operation")
class HistoryInsertGQLModel:
    name: str = strawberry.field(description="history name")
    request_id: uuid.UUID = strawberry.field(description="id of request")
    form_id: uuid.UUID = strawberry.field(description="id of form")

    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    createdby: strawberry.Private[uuid.UUID] = None    

@strawberry.input(description="Input structure - U operation")
class HistoryUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")

    name: typing.Optional[str] = strawberry.field(description="history name", default=None)
    changedby: strawberry.Private[uuid.UUID] = None

@strawberry.type(description="Result of CU operations")
class HistoryResultGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key of CU operation object")
    msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
For update operation fail should be also stated when bad lastchange has been entered.""")

    @strawberry.field(description="Object of CU operation, final version")
    async def history(self, info: strawberry.types.Info) -> HistoryGQLModel:
        result = await HistoryGQLModel.resolve_reference(info=info, id=self.id)
        return result

@strawberry.mutation(
    description="C operation",
    permission_classes=[OnlyForAuthentized])
async def history_insert(self, info: strawberry.types.Info, history: HistoryInsertGQLModel) -> HistoryResultGQLModel:
    user = getUserFromInfo(info)
    history.createdby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).histories
    row = await loader.insert(history)
    result = HistoryResultGQLModel(id=row.id, msg="ok")
    result.msg = "ok"
    result.id = row.id
    return result

@strawberry.mutation(
    description="U operation",
    permission_classes=[OnlyForAuthentized])
async def history_update(self, info: strawberry.types.Info, history: HistoryUpdateGQLModel) -> HistoryResultGQLModel:
    user = getUserFromInfo(info)
    history.changedby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).histories
    row = await loader.update(history)
    result = HistoryResultGQLModel(id=history.id, msg="ok")
    result.msg = "fail" if row is None else "ok"
    result.id = history.id
    return result   