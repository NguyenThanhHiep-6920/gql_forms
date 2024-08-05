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
PartGQLModel = Annotated["PartGQLModel", strawberry.lazy(".PartGQLModel")]

@strawberry.federation.type(
    keys=["id"], 
    name="FormSectionGQLModel",
    description="""Type representing a section in the form"""
)
class SectionGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).sections
    
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
        description="""Section's order""",
        permission_classes=[OnlyForAuthentized])
    def order(self) -> int:
        return self.order if self.order else 0

    @strawberry.field(
        description="Retrieves the parts related to this section",
        permission_classes=[OnlyForAuthentized])
    async def parts(self, info: strawberry.types.Info) -> typing.List["PartGQLModel"]:
        loader = getLoadersFromInfo(info).parts
        result = await loader.filter_by(section_id=self.id)
        return result

    @strawberry.field(
        description="Retrieves the form owing this section",
        permission_classes=[OnlyForAuthentized])
    async def form(self, info: strawberry.types.Info) -> typing.Optional["FormGQLModel"]:
        from .FormGQLModel import FormGQLModel
        result = await FormGQLModel.resolve_reference(info, self.form_id)
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
class SectionWhereFilter:
    name: str
    name_en: str
    valid: bool
    type_id: uuid.UUID
    createdby: uuid.UUID

    from .FormGQLModel import FormWhereFilter
    form: FormWhereFilter

# resolve_sectionsForForm = createAttributeVectorResolver(
#     scalarType=SectionGQLModel, 
#     whereFilterType=SectionWhereFilter, 
#     foreignKeyName="from_id", description="Gets sections associated with form",
#     loaderLambda=lambda info: getLoadersFromInfo(info=info).sections
#     )
    
@strawberry.field(
    description="returns section from form by its id",
    permission_classes=[OnlyForAuthentized])
async def form_section_by_id(self, info: strawberry.types.Info, id: uuid.UUID) -> typing.Optional[SectionGQLModel]:
    return await SectionGQLModel.resolve_reference(info=info, id=id)
#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Input structure - C operation")
class SectionInsertGQLModel:
    name: str = strawberry.field(description="Section name")
    form_id: uuid.UUID = strawberry.field(description="id of parent entity")

    name_en: typing.Optional[str] = strawberry.field(description="Section english name", default=None)
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    order: typing.Optional[int] = strawberry.field(description="Position in parent entity", default=None)
    valid: typing.Optional[bool] = None
    createdby: strawberry.Private[uuid.UUID] = None 
    rbacobject: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Input structure - U operation")
class SectionUpdateGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")

    name: typing.Optional[str] = strawberry.field(description="Section name", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Section english name", default=None)
    order: typing.Optional[int] = strawberry.field(description="Position in parent entity", default=None)
    valid: typing.Optional[bool] = None
    changedby: strawberry.Private[uuid.UUID] = None

@strawberry.type(description="Result of CU operations")
class SectionResultGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key of CU operation object")
    msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
For update operation fail should be also stated when bad lastchange has been entered.""")

    @strawberry.field(description="Object of CU operation, final version")
    async def section(self, info: strawberry.types.Info) -> SectionGQLModel:
        return await SectionGQLModel.resolve_reference(info, self.id)

@strawberry.mutation(
    description="C operation",
    permission_classes=[OnlyForAuthentized])
async def section_insert(self, info: strawberry.types.Info, section: SectionInsertGQLModel) -> SectionResultGQLModel:
    user = getUserFromInfo(info)
    section.createdby = uuid.UUID(user["id"])

    # form as the parent of new section is checked
    # rbacobject is retrieved and assigned to section.rbacobject
    # rbacobject is shared among form and its sections
    formloader = getLoadersFromInfo(info).forms
    form = await formloader.load(section.form_id)
    assert form is not None, f"{section.form_id} is unknown form (during section insert)"
    section.rbacobject = form.rbacobject

    loader = getLoadersFromInfo(info).sections
    row = await loader.insert(section)
    result = SectionResultGQLModel(id=section.id, msg="fail")
    result.msg = "ok"
    result.id = row.id
    print("section_insert", result)
    return result

@strawberry.mutation(
    description="U operation",
    permission_classes=[OnlyForAuthentized])
async def section_update(self, info: strawberry.types.Info, section: SectionUpdateGQLModel) -> SectionResultGQLModel:
    user = getUserFromInfo(info)
    section.changedby = uuid.UUID(user["id"])

    loader = getLoadersFromInfo(info).sections
    row = await loader.update(section)
    result = SectionResultGQLModel(id=section.id, msg="fail")
    result.msg = "fail" if row is None else "ok"
    result.id = section.id
    return result   