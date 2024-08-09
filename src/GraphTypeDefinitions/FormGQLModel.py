import strawberry
import typing
import datetime
import uuid
import logging

from typing import Annotated
# from src.utils.Dataloaders import getLoadersFromInfo, getUserFromInfo
from uoishelpers.resolvers import getLoadersFromInfo, getUserFromInfo
from .BaseGQLModel import BaseGQLModel

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
    # createRootResolver_by_page,
    # createAttributeScalarResolver,
    # createAttributeVectorResolver
)
from ._GraphPermissions import RoleBasedPermission, OnlyForAuthentized

SectionGQLModel = Annotated["SectionGQLModel", strawberry.lazy(".SectionGQLModel")]
FormTypeGQLModel = Annotated["FormTypeGQLModel", strawberry.lazy(".FormTypeGQLModel")]
UserGQLModel = Annotated["UserGQLModel", strawberry.lazy(".externals")]
StateGQLModel = Annotated["StateGQLModel", strawberry.lazy(".externals")]
RequestGQLModel = Annotated["RequestGQLModel", strawberry.lazy(".RequestGQLModel")]

FormGQLModelDescription = """
# Reason

Entity representing a form, form is digitalized A4 sheet

## Structure

form -> sections -> parts -> items
"""

@strawberry.federation.type(
    keys=["id"], description=FormGQLModelDescription
)
class FormGQLModel(BaseGQLModel):
    """
    Type representing a request in the system.
    This class extends the base `RequestModel` from the database and adds additional fields and methods needed for use in GraphQL.
    """
    @classmethod
    def getLoader(cls, info):
        loader = getLoadersFromInfo(info).forms
        # logging.info(f"FormGQLModel.getLoader => {loader}")
        return loader
    
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
        description="""Form's validity""",
        permission_classes=[OnlyForAuthentized])
    def valid(self) -> bool:
        return self.valid

    @strawberry.field(
        description="""Form's status""",
        permission_classes=[OnlyForAuthentized])
    def status(self) -> typing.Optional[str]:
        return self.status

    # @strawberry.field(
    #     description="Retrieves the sections related to this form (form has several sections), form->section->part->item",
    #     permission_classes=[OnlyForAuthentized],
    #     # extensions=[strawberry.permission.PermissionExtension(fail_silently=True, permissions=[RoleBasedPermission(roles="administrator")])]
    #     )
    # async def sections(
    #     self, info: strawberry.types.Info,
    # ) -> typing.List["SectionGQLModel"]:
    #     print(info)
    #     loader = getLoadersFromInfo(info).sections
    #     sections = await loader.filter_by(form_id=self.id)
    #     return sections

    # from ._GraphResolvers import asForeignList

    @strawberry.field(
        description="Retrieves the sections related to this form (form has several sections), form->section->part->item",
        permission_classes=[OnlyForAuthentized],
        )
    async def sections(
        self, info: strawberry.types.Info,
    ) -> typing.List["SectionGQLModel"]:
        loader = getLoadersFromInfo(info).sections
        results = await loader.filter_by(form_id=self.id)
        return results

    # @strawberry.field(
    #     description="Retrieves the user who has initiated this request",
    #     permission_classes=[OnlyForAuthentized])
    # async def creator(self, info: strawberry.types.Info) -> typing.Optional["UserGQLModel"]:
    #     #user = UserGQLModel(id=self.createdby)
    #     from .externals import UserGQLModel
    #     result = (None 
    #         if self.createdby is None else 
    #         await UserGQLModel.resolve_reference(id=self.createdby)
    #     )
    #     return result

    @strawberry.field(
        description="State od the form",
        permission_classes=[OnlyForAuthentized])
    async def state(self, info: strawberry.types.Info) -> typing.Optional["StateGQLModel"]:
        #user = UserGQLModel(id=self.createdby)
        from .externals import StateGQLModel
        return await StateGQLModel.resolve_reference(info=info, id=self.state_id)

    # state_id = UUIDFKey(nullable=True, comment="state of the request")

    @strawberry.field(
        description="Retrieves the type of form",
        permission_classes=[OnlyForAuthentized])
    async def type(self, info: strawberry.types.Info) -> typing.Optional["FormTypeGQLModel"]:
        from .FormTypeGQLModel import FormTypeGQLModel
        result = await FormTypeGQLModel.resolve_reference(info, id=self.type_id)
        return result
  
    @strawberry.field(
        description="Retrieves the type of form",
        permission_classes=[OnlyForAuthentized])
    async def request(self, info: strawberry.types.Info) -> typing.Optional["RequestGQLModel"]:
        from .HistoryGQLModel import HistoryGQLModel
        loader = HistoryGQLModel.getLoader(info)
        rows = await loader.filter_by(form_id=self.id)
        row = next(rows, None)

        from .RequestGQLModel import RequestGQLModel
        result =  await RequestGQLModel.resolve_reference(info, row.request_id)
        return None if row is None else result
    
#############################################################
#
# Queries
#
#############################################################
from ._GraphPermissions import OnlyForAuthentized
@strawberry.field(
    description="Retrieves the form type",
    permission_classes=[OnlyForAuthentized])
async def form_by_id(
    self, info: strawberry.types.Info, id: uuid.UUID
) -> typing.Optional[FormGQLModel]:
    # logging.info(f"form_by_id ({id})")
    result = await FormGQLModel.resolve_reference(info=info, id=id)
    # logging.info(f"form_by_id ({result})")
    return result

from dataclasses import dataclass
from uoishelpers.resolvers import createInputs

# FormTypeWhereFilter_ = typing.Annotated["FormTypeWhereFilter", strawberry.lazy(".FormTypeGQLModel")]
@createInputs
@dataclass
class FormWhereFilter:
    name: str
    name_en: str
    valid: bool
    type_id: uuid.UUID
    createdby: uuid.UUID

    from .FormTypeGQLModel import FormTypeWhereFilter
    type: FormTypeWhereFilter

# @strawberry.field(
#     description="Retrieves the form type",
#     permission_classes=[OnlyForAuthentized])
# async def form_page(
#     self, info: strawberry.types.Info, skip: int = 0, limit: int = 10,
#     where: typing.Optional[FormWhereFilter] = None
# ) -> typing.List[FormGQLModel]:
#     # print(info)
#     # context = info.context
#     # request = context["request"]
#     # user = request.scope["user"]
#     # print(user)
#     wf = None if where is None else strawberry.asdict(where)
#     loader = getLoadersFromInfo(info).forms
#     result = await loader.page(skip, limit, where=wf)
#     return result    

from src.DBResolvers import FormResolvers
form_page = strawberry.field(
    description="Retrieves the form type",
    permission_classes=[OnlyForAuthentized],
    resolver=FormResolvers.Page(GQLModel=FormGQLModel, WhereFilterModel=FormWhereFilter))

# from ._GraphResolvers import asPage

# @strawberry.field(
#     description="Retrieves the form type",
#     permission_classes=[OnlyForAuthentized])
# @asPage
# async def form_page(
#     self, info: strawberry.types.Info, skip: int = 0, limit: int = 10,
#     where: typing.Optional[FormWhereFilter] = None
# ) -> typing.List[FormGQLModel]:
#     return getLoadersFromInfo(info).forms



#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Input structure - C operation")
class FormInsertGQLModel:
    name: str = strawberry.field(description="form name")
    type_id: uuid.UUID = strawberry.field(description="form type")
    rbacobject: typing.Optional[uuid.UUID] = strawberry.field(
        description="user_id or group_id, allows resolution of authorized users, if not present, logged user will be assigned", default=None)
    
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="form name", default=None)
    type_id: typing.Optional[uuid.UUID] = None
    valid: typing.Optional[bool] = True
    createdby: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Input structure - U operation")
class FormUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")

    name: typing.Optional[str] = strawberry.field(description="form name", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="form name", default=None)
    type_id: typing.Optional[uuid.UUID] = strawberry.field(description="form type", default=None)
    valid: typing.Optional[bool] = None
    changedby: strawberry.Private[uuid.UUID] = None
    
    
@strawberry.type(description="Result of CU operations")
class FormResultGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key of CU operation object")
    msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
For update operation fail should be also stated when bad lastchange has been entered.""")

    @strawberry.field(description="""Result of form operation""")
    async def form(self, info: strawberry.types.Info) -> typing.Optional[FormGQLModel]:
        result = await FormGQLModel.resolve_reference(info, self.id)
        return result
   
from ._GraphPermissions import OnlyForAuthentized
from uoishelpers.resolvers import encapsulateInsert, encapsulateUpdate, encapsulateDelete

@strawberry.mutation(
    description="C operation",
    permission_classes=[OnlyForAuthentized])
async def form_insert(self, info: strawberry.types.Info, form: FormInsertGQLModel) -> FormResultGQLModel:
    result = FormResultGQLModel(id=form.id, msg="ok")
    result = await encapsulateInsert(info=info, loader=FormGQLModel.getLoader(info=info), entity=form, result=result)
    return result

@strawberry.mutation(
    description="U operation",
    permission_classes=[OnlyForAuthentized])
async def form_update(self, info: strawberry.types.Info, form: FormUpdateGQLModel) -> FormResultGQLModel:
    user = getUserFromInfo(info)
    form.changedby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).forms
    row = await loader.update(form)
    result = FormResultGQLModel(id=form.id, msg="ok")
    result.msg = "fail" if row is None else "ok"
    result.id = form.id
        
    return result   