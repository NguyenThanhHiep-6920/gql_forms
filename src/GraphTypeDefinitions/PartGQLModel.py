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

SectionGQLModel = Annotated["SectionGQLModel", strawberry.lazy(".SectionGQLModel")]
ItemGQLModel = Annotated["ItemGQLModel", strawberry.lazy(".ItemGQLModel")]

@strawberry.federation.type(
    keys=["id"], 
    name="FormPartGQLModel",
    description="""Type representing a part in the section"""
)
class PartGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).parts
    
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
        description="""Part's order""",
        permission_classes=[OnlyForAuthentized])
    def order(self) -> int:
        return self.order if self.order else 0

    @strawberry.field(
        description="Retrieves the section owning this part",
        permission_classes=[OnlyForAuthentized])
    async def section(self, info: strawberry.types.Info) -> typing.Optional["SectionGQLModel"]:
        from .SectionGQLModel import SectionGQLModel
        result = await SectionGQLModel.resolve_reference(info, self.section_id)
        return result

    @strawberry.field(
        description="Retrieves the items related to this part",
        permission_classes=[OnlyForAuthentized])
    async def items(self, info: strawberry.types.Info) -> typing.List["ItemGQLModel"]:
        loader = getLoadersFromInfo(info).items
        result = await loader.filter_by(part_id=self.id)
        return result

#############################################################
#
# Queries
#
#############################################################
# @strawberry.field(description="")
# async def form_part_by_id(self, info: strawberry, id: strawberry.uuid) -> "PartGQLModel":
#     loader = getLoadersFromInfo(info).parts
#     result = await loader.load(id)
#     return result

@strawberry.field(
    description="returns part of section by its id",
    permission_classes=[OnlyForAuthentized])
async def form_part_by_id(self, info: strawberry.types.Info, id: uuid.UUID) -> typing.Optional[PartGQLModel]:
    return await PartGQLModel.resolve_reference(info=info, id=id)
#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Input structure - C operation")
class FormPartInsertGQLModel:
    name: str = strawberry.field(description="Part name")
    section_id: uuid.UUID
    name_en: typing.Optional[str] = strawberry.field(description="English part name", default=None)
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    order: typing.Optional[int] = strawberry.field(description="Position in parent entity", default=None)
    createdby: strawberry.Private[uuid.UUID] = None 
    rbacobject: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Input structure - U operation")
class FormPartUpdateGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    section_id: typing.Optional[uuid.UUID] = strawberry.field(description="id of parent entity", default=None)
    name: typing.Optional[str] = strawberry.field(description="Part name", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English part name", default=None)
    order: typing.Optional[int] = strawberry.field(description="Position in parent entity", default=None)
    changedby: strawberry.Private[uuid.UUID] = None

@strawberry.type(description="Result of CU operations")
class FormPartResultGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key of CU operation object")
    msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
For update operation fail should be also stated when bad lastchange has been entered.""")

    @strawberry.field(description="Object of CU operation, final version")
    async def part(self, info: strawberry.types.Info) -> PartGQLModel:
        result = await PartGQLModel.resolve_reference(info=info, id=self.id)
        return result

@strawberry.field(
    description="C operation",
    permission_classes=[OnlyForAuthentized])
async def part_insert(self, info: strawberry.types.Info, part: FormPartInsertGQLModel) -> FormPartResultGQLModel:
    user = getUserFromInfo(info)
    part.createdby = uuid.UUID(user["id"])

    # form as the parent of new section is checked
    # rbacobject is retrieved and assigned to section.rbacobject
    # rbacobject is shared among form, its sections and parts
    sectionloader = getLoadersFromInfo(info).sections
    section = await sectionloader.load(part.section_id)
    assert section is not None, f"{part.section_id} is unknown section (of form) (during part insert)"
    part.rbacobject = section.rbacobject

    result = FormPartResultGQLModel(id=part.id, msg="fail")
    loader = getLoadersFromInfo(info).parts
    row = await loader.insert(part)
    if row:
        result.msg = "ok"
        result.id = row.id
    return result

@strawberry.field(
    description="U operation",
    permission_classes=[OnlyForAuthentized])
async def part_update(self, info: strawberry.types.Info, part: FormPartUpdateGQLModel) -> FormPartResultGQLModel:
    user = getUserFromInfo(info)
    part.changedby = uuid.UUID(user["id"])
    result = FormPartResultGQLModel(id=part.id, msg="fail")
    loader = getLoadersFromInfo(info).parts
    row = await loader.update(part)
    if row:
        result.msg = "ok"
    return result
