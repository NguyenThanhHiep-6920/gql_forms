import strawberry
import datetime
import typing
import uuid

from typing import Annotated

from utils.Dataloaders import getLoadersFromInfo, getUserFromInfo
from .BaseGQLModel import BaseGQLModel

from GraphTypeDefinitions._GraphResolvers import (
    resolve_id,
    resolve_name,
    resolve_name_en,
    resolve_changedby,
    resolve_created,
    resolve_lastchange,
    resolve_createdby,
    createRootResolver_by_id,
    createRootResolver_by_page,
    createAttributeScalarResolver,
    createAttributeVectorResolver
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

    @strawberry.field(description="""Part's order""")
    def order(self) -> int:
        return self.order

    @strawberry.field(description="Retrieves the section owning this part")
    async def section(self, info: strawberry.types.Info) -> typing.Optional["SectionGQLModel"]:
        from .SectionGQLModel import SectionGQLModel
        result = await SectionGQLModel.resolve_reference(info, self.section_id)
        return result

    @strawberry.field(description="Retrieves the items related to this part")
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

#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="")
class FormPartInsertGQLModel:
    name: str = strawberry.field(description="Part name")
    section_id: uuid.UUID
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    order: typing.Optional[int] = strawberry.field(description="Position in parent entity", default=None)
    createdby: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="")
class FormPartUpdateGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    section_id: typing.Optional[uuid.UUID] = strawberry.field(description="id of parent entity", default=None)
    name: typing.Optional[str] = strawberry.field(description="Part name", default=None)
    order: typing.Optional[int] = strawberry.field(description="Position in parent entity", default=None)
    changedby: strawberry.Private[uuid.UUID] = None

@strawberry.type(description="")
class FormPartResultGQLModel:
    id: uuid.UUID
    msg: str

    @strawberry.field(description="")
    async def part(self, info: strawberry.types.Info) -> PartGQLModel:
        result = await PartGQLModel.resolve_reference(info=info, id=self.id)
        return result

@strawberry.field(description="")
async def part_insert(self, info: strawberry.types.Info, part: FormPartInsertGQLModel) -> FormPartResultGQLModel:
    user = getUserFromInfo(info)
    part.createdby = uuid.UUID(user["id"])
    result = FormPartResultGQLModel(id=part.id, msg="fail")
    loader = getLoadersFromInfo(info).parts
    row = await loader.insert(part)
    if row:
        result.msg = "ok"
        result.id = row.id
    return result

@strawberry.field(description="")
async def part_update(self, info: strawberry.types.Info, part: FormPartUpdateGQLModel) -> FormPartResultGQLModel:
    user = getUserFromInfo(info)
    part.changedby = uuid.UUID(user["id"])
    result = FormPartResultGQLModel(id=part.id, msg="fail")
    loader = getLoadersFromInfo(info).parts
    row = await loader.update(part)
    if row:
        result.msg = "ok"
    return result
