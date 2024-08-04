import strawberry
import datetime
import typing
import uuid
import logging

from typing import Annotated

from uoishelpers.resolvers import getLoadersFromInfo, getUserFromInfo

from ._GraphPermissions import RoleBasedPermission
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

UserGQLModel = Annotated["UserGQLModel", strawberry.lazy(".externals")]
HistoryGQLModel = Annotated["HistoryGQLModel", strawberry.lazy(".HistoryGQLModel")]


# define the type help to get attribute name and name
@strawberry.federation.type(
    keys=["id"], description="""Entity representing a request (digital form of a paper, aka "student request to the dean")""",
    
)
class RequestGQLModel(BaseGQLModel):
    """
    Type representing a request in the system.
    This class extends the base `RequestModel` from the database and adds additional fields and methods needed for use in GraphQL.
    """
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).requests
    
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

    # @strawberry.field(
    #     description="""Permitted attribute""",
    #     # extensions=[strawberry.permission.PermissionExtension(fail_silently=True, permissions=[RoleBasedPermission(roles="rector")])]
    #     permission_classes=[RoleBasedPermission(roles="rector", whatreturn=None)]
    #     )
    # def permitted() -> typing.Optional[str]:
    #     return "OK"

    @strawberry.field(
        description="""Request's time of last update""",
        permission_classes=[OnlyForAuthentized()])
    def creator(self) -> typing.Optional["UserGQLModel"]:
        from .externals import UserGQLModel
        #result = await UserGQLModel.resolve_reference(id=self.createdby)
        return UserGQLModel(id=self.createdby)

    @strawberry.field(
        description="""Request's time of last update""",
        permission_classes=[OnlyForAuthentized(isList=True)])
    async def histories(self, info: strawberry.types.Info) -> typing.List["HistoryGQLModel"]:
        loader = getLoadersFromInfo(info).histories
        result = await loader.filter_by(request_id=self.id)
        return result
    
#############################################################
#
# Queries
#
#############################################################
from dataclasses import dataclass
from uoishelpers.resolvers import createInputs

@createInputs
@dataclass
class RequestWhereFilter:
    name: str
    name_en: str
    createdby: uuid.UUID

@strawberry.field(
    description="""Finds an request by their id""",
    permission_classes=[OnlyForAuthentized()])
async def request_by_id(
    self, info: strawberry.types.Info, id: uuid.UUID
) -> typing.Optional[RequestGQLModel]:
    result = await RequestGQLModel.resolve_reference(info, id)
    return result

# requests_page = createRootResolver_by_page(
#     scalarType=RequestGQLModel,
#     whereFilterType=RequestWhereFilter,
#     description="Retrieves all requests",
#     loaderLambda=lambda info: getLoadersFromInfo(info).requests,
#     skip=0,
#     limit=10
#     )
from src.DBResolvers import RequestResolvers
# from ._GraphResolvers import asPage

# @strawberry.field(
#     description="Retrieves all requests",
#     permission_classes=[OnlyForAuthentized(isList=True)])
# @asPage
# #async def request_page(self, info: strawberry.types.Info, where: typing.Optional[RequestWhereFilter] = None) -> typing.List[RequestGQLModel]:
# async def request_page(self, info: strawberry.types.Info, where: typing.Optional[RequestWhereFilter]) -> typing.List[RequestGQLModel]:
#     logging.info("returning just loader")
#     return getLoadersFromInfo(info).requests

request_page = strawberry.field(
    description="Retrieves all requests",
    permission_classes=[OnlyForAuthentized(isList=True)],
    resolver=RequestResolvers.Page(GQLModel=RequestGQLModel, WhereFilterModel=RequestWhereFilter)
)
#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Input structure - C operation")
class FormRequestInsertGQLModel:
    name: str = strawberry.field(description="Request name")
    #form_type_id: uuid.UUID = strawberry.field(description="Form type which will be initialized")
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    createdby: strawberry.Private[uuid.UUID] = None 
    rbacobject: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Input structure - U operation")
class FormRequestUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")
    name: typing.Optional[str] = strawberry.field(description="Request name", default=None)
    changedby: strawberry.Private[uuid.UUID] = None

@strawberry.type(description="Result of CU operations")
class FormRequestResultGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key of CU operation object")
    msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
For update operation fail should be also stated when bad lastchange has been entered.""")

    @strawberry.field(description="Object of CU operation, final version")
    async def request(self, info: strawberry.types.Info) -> RequestGQLModel:
        return await RequestGQLModel.resolve_reference(info, self.id)

@strawberry.mutation(
    description="C operation",
    permission_classes=[OnlyForAuthentized()])
async def form_request_insert(self, info: strawberry.types.Info, request: FormRequestInsertGQLModel) -> FormRequestResultGQLModel:
    user = getUserFromInfo(info)
    request.createdby = uuid.UUID(user["id"])
    request.rbacobject = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).requests
    row = await loader.insert(request)
    result = FormRequestResultGQLModel(id=row.id, msg="ok")
    result.msg = "ok"
    result.id = row.id
    return result

@strawberry.mutation(
    description="U operation",
    permission_classes=[OnlyForAuthentized()])
async def form_request_update(self, info: strawberry.types.Info, request: FormRequestUpdateGQLModel) -> FormRequestResultGQLModel:
    user = getUserFromInfo(info)
    request.changedby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).requests
    row = await loader.update(request)
    result = FormRequestResultGQLModel(id=request.id, msg="ok")
    result.msg = "fail" if row is None else "ok"
    result.id = request.id
    return result   