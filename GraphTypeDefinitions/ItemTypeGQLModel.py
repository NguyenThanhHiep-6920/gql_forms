import strawberry
import typing
import datetime
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

ItemCategoryGQLModel = Annotated["ItemCategoryGQLModel", strawberry.lazy(".ItemCategoryGQLModel")]

@strawberry.federation.type(
    keys=["id"], 
    name="FormItemTypeGQLModel",
    description="""Type representing an item type"""
)
class ItemTypeGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).itemtypes
    
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

    @strawberry.field(description="""Type category""")
    async def category(self, info: strawberry.types.Info) -> typing.Optional["ItemCategoryGQLModel"]:
        from .ItemCategoryGQLModel import ItemCategoryGQLModel
        return await ItemCategoryGQLModel.resolve_reference(info=info, id=self.category_id)
    
#############################################################
#
# Queries
#
#############################################################

@strawberry.field(description="Retrieves the item types")
async def item_type_page(
    self, info: strawberry.types.Info, skip: int = 0, limit: int = 10
) -> typing.List[ItemCategoryGQLModel]:
    loader = getLoadersFromInfo(info).itemtypes
    result = await loader.page(skip=skip, limit=limit)
    return result


@strawberry.field(description="Retrieves the item type")
async def item_type_by_id(
    self, info: strawberry.types.Info, id: uuid.UUID
) -> typing.Optional[ItemTypeGQLModel]:
    result = await ItemTypeGQLModel.resolve_reference(info=info, id=id)
    return result

#############################################################
#
# Mutations
#
#############################################################


@strawberry.input(description="")
class FormItemTypeInsertGQLModel:
    name: str = strawberry.field(description="Item type name")
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    createdby: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="")
class FormItemTypeUpdateGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    name: typing.Optional[str] = strawberry.field(description="Item type name", default=None)
    order: typing.Optional[int] = None
    changedby: strawberry.Private[uuid.UUID] = None


@strawberry.type(description="")
class FormItemTypeResultGQLModel:
    id: uuid.UUID
    msg: str

    @strawberry.field(description="")
    async def item_type(self, info: strawberry.types.Info) -> "ItemTypeGQLModel":
        result = await ItemTypeGQLModel.resolve_reference(info, self.id)
        return result

@strawberry.mutation(description="")
async def form_item_type_insert(self, info: strawberry.types.Info, item_type: FormItemTypeInsertGQLModel) -> FormItemTypeResultGQLModel:
    user = getUserFromInfo(info)
    item_type.createdby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).itemtypes
    row = await loader.insert(item_type)
    result = FormItemTypeResultGQLModel(msg="fail", id=None)
    result.msg = "fail" if row is None else "ok"
    result.id = None if row is None else row.id       
    return result


@strawberry.mutation
async def form_item_type_update(self, info: strawberry.types.Info, item_type: FormItemTypeUpdateGQLModel) -> FormItemTypeResultGQLModel:
    user = getUserFromInfo(info)
    item_type.changedby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).itemtypes
    row = await loader.update(item_type)
    result = FormItemTypeResultGQLModel(msg="fail", id=None)
    result.msg = "fail" if row is None else "ok"
    result.id = item_type.id       
    return result