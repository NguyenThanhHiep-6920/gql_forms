import strawberry
import datetime
import typing
import uuid
import asyncio
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
StateGQLModel = Annotated["StateGQLModel", strawberry.lazy(".externals")]


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

    @strawberry.field(
        description="Retrieves the user who has initiated this request",
        permission_classes=[OnlyForAuthentized()])
    async def state(self, info: strawberry.types.Info) -> typing.Optional["StateGQLModel"]:
        #user = UserGQLModel(id=self.createdby)
        from .externals import StateGQLModel
        return await StateGQLModel.resolve_reference(info=info, id=self.state_id)
    
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

@strawberry.input(description="Input structure")
class FormRequestUseTransitionGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")
    transition_id: uuid.UUID = strawberry.field(description="transition used for this operation")
    history_message: str = strawberry.field(description="this will appear in history records")
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


from strawberry.extensions import FieldExtension


class TestExtension(FieldExtension):
    async def resolve_async(
        self, next: typing.Callable[..., typing.Any], source: typing.Any, info: strawberry.Info, **kwargs
    ):
        print("TestExtension", source, type(source), info, kwargs, flush=True)
        result = await next(source, info, **kwargs)
        print("TestExtension.result", result, flush=True)
        return result

@strawberry.field(
    description="U operation",
    extensions=[TestExtension()]
    )
async def form_test_extension(self, info: strawberry.types.Info, param: typing.Optional[str] = "default") -> typing.Optional[FormRequestResultGQLModel]:
    print("form_test_extension", param, flush=True)
    return None

@strawberry.mutation(
    description="U operation",
    permission_classes=[OnlyForAuthentized()],
    )
async def form_request_use_transition(self, info: strawberry.types.Info, request: FormRequestUseTransitionGQLModel) -> FormRequestResultGQLModel:
    # create copy of current form
    # make row in histories
    # change state of request

    user = getUserFromInfo(info)
    request.changedby = uuid.UUID(user["id"])

    # create copy of current form
    request_loader = RequestGQLModel.getLoader(info=info)
    request_row = await request_loader.load(request.id)
    assert request_row is not None, f"request.id {request.id} refers to unknown request"
    form_id = request_row.form_id
    from .FormGQLModel import FormGQLModel
    formloader = FormGQLModel.getLoader(info=info)
    form_row = await formloader.load(form_id)
    assert form_row is not None, f"Unexpected situation, form has not been found on request {request.id}"
    copy_form_id = uuid.uuid1()
    copy_form = await formloader.insert(entity=form_row, extraAttributes={"id": copy_form_id})
    
    from .SectionGQLModel import SectionGQLModel
    section_loader = SectionGQLModel.getLoader(info=info)
    sections = await section_loader.filter_by(form_id=form_id)
    section_ids = list(map(lambda section: section.id, sections))
    assert len(section_ids) !=0, f"request's {request.id} form has no sections :("
    copy_sections = (section_loader.insert(entity=section, extraAttributes={"id": uuid.uuid1(), "form_id": copy_form_id})  for section in sections)
    copy_sections = await asyncio.gather(*copy_sections)
    sections_map = {copy_section.id: oldid for copy_section, oldid in zip(copy_sections, section_ids)}

    from .PartGQLModel import PartGQLModel
    part_loader = PartGQLModel.getLoader(info=info)
    part_db_model = part_loader.getModel()
    
    parts_select_statement = part_loader.getSelectStatement()
    parts_select_statement = parts_select_statement.filter(part_db_model.section_id.in_(section_ids))
    parts = await part_loader.execute_select(parts_select_statement)
    part_ids = list(map(lambda part: part.id, parts))
    copy_parts = (part_loader.insert(entity=part, extraAttributes={"id": uuid.uuid1(), "section_id": sections_map[part.section_id]}) for part in parts)
    copy_parts = await asyncio.gather(*copy_parts)
    parts_map = {copy_part.id: oldid for copy_part, oldid in zip(copy_parts, part_ids)}
    # copy_part_ids = {id: uuid.uuid1() for id in part_ids}

    from .ItemGQLModel import ItemGQLModel
    item_loader = ItemGQLModel.getLoader(info=info)
    item_db_model = item_loader.getModel()
    items_select_statement = item_loader.getSelectStatement()
    items_select_statement = items_select_statement.filter(item_db_model.part_id.in_(part_ids))
    items = await item_loader.execute_select(items_select_statement)
    # item_ids = list(map(lambda item: item.id, items))
    copy_items = (item_loader.insert(entity=item, extraAttributes={"id": uuid.uuid1(), "part_id": parts_map[item.part_id]}) for item in items )
    copy_items = await asyncio.gather(*copy_items)
    # copy_item_ids = {id: uuid.uuid1() for id in item_ids}

    # make row in histories
    from .HistoryGQLModel import HistoryGQLModel
    history_loader = HistoryGQLModel.getLoader(info=info)
    history_row = await history_loader.insert(
        None, 
        extraAttributes={
            "id": uuid.uuid1(), 
            "form_id": form_id, 
            "request_id": request.id, 
            "name": request.history_message}
    )

    # change state of request
    updated_request_row = await request_loader.update(request_row, extraAttributes={"state_id": target_state_id})

    result = FormRequestResultGQLModel(id=request.id, msg="ok")
    result.msg = "fail" if updated_request_row is None else "ok"
    result.id = request.id
    return result   


