import strawberry
import typing
import datetime
import uuid

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

ItemTypeGQLModel = typing.Annotated["ItemTypeGQLModel", strawberry.lazy(".ItemTypeGQLModel")]

@strawberry.federation.type(
    keys=["id"], 
    name="FormItemCategoryGQLModel",
    description="""Type representing an item category"""
)
class ItemCategoryGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).itemcategories
    
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
        description="Returns all type for this category",
        permission_classes=[OnlyForAuthentized])
    async def types(self, info: strawberry.types.Info) -> typing.List["ItemTypeGQLModel"]:
        loader = getLoadersFromInfo(info).itemtypes
        rows = await loader.filter_by(category_id=self.id)
        return rows   

#############################################################
#
# Queries
#
#############################################################
from src.DBResolvers import ItemCategoryResolvers

from dataclasses import dataclass
from uoishelpers.resolvers import createInputs

@createInputs
@dataclass
class FormItemCategoryWhereFilter:
    id: uuid.UUID
    name: str
    category_id: uuid.UUID


# @strawberry.field(
#     description="Retrieves the item categories",
#     permission_classes=[OnlyForAuthentized])
# async def item_category_page(
#     self, info: strawberry.types.Info, skip: int = 0, limit: int = 10
# ) -> typing.List[ItemCategoryGQLModel]:
#     loader = getLoadersFromInfo(info).itemcategories
#     result = await loader.page(skip=skip, limit=limit)
#     return result

item_category_page = strawberry.field(
    description="Retrieves the item categories",
    resolver=ItemCategoryResolvers.Page(GQLModel=ItemCategoryGQLModel, WhereFilterModel=FormItemCategoryWhereFilter),
    permission_classes=[
        OnlyForAuthentized
        ]
    )

@strawberry.field(
    description="Retrieves the item category",
    permission_classes=[OnlyForAuthentized])
async def item_category_by_id(
    self, info: strawberry.types.Info, id: uuid.UUID
) -> typing.Optional[ItemCategoryGQLModel]:
    result = await ItemCategoryGQLModel.resolve_reference(info=info, id=id)
    return result

#############################################################
#
# Mutations
#
#############################################################


@strawberry.input(description="Input structure - C operation")
class FormItemCategoryInsertGQLModel:
    name: str = strawberry.field(description="Item category name")
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    createdby: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Input structure - U operation")
class FormItemCategoryUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")

    name: typing.Optional[str] = strawberry.field(description="Item category name", default=None)
    changedby: strawberry.Private[uuid.UUID] = None

@strawberry.type(description="Result of CU operations")
class FormItemCategoryResultGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key of CU operation object")
    msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
For update operation fail should be also stated when bad lastchange has been entered.""")

    @strawberry.field(description="Object of CU operation, final version")
    async def category(self, info: strawberry.types.Info) -> ItemCategoryGQLModel:
        result = await ItemCategoryGQLModel.resolve_reference(info=info, id=self.id)
        return result

@strawberry.mutation(
    description="C operation",
    permission_classes=[OnlyForAuthentized])
async def item_category_insert(self, info: strawberry.types.Info, item_category: FormItemCategoryInsertGQLModel) -> FormItemCategoryResultGQLModel:
    user = getUserFromInfo(info)
    item_category.createdby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).itemcategories
    row = await loader.insert(item_category)
    result = FormItemCategoryResultGQLModel(id=row.id, msg="ok")
    result.msg = "ok"
    result.id = row.id
    return result

@strawberry.mutation(
    description="U operation",
    permission_classes=[OnlyForAuthentized])
async def item_category_update(self, info: strawberry.types.Info, item_category: FormItemCategoryUpdateGQLModel) -> FormItemCategoryResultGQLModel:
    user = getUserFromInfo(info)
    item_category.changedby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).itemcategories
    row = await loader.update(item_category)
    result = FormItemCategoryResultGQLModel(id=item_category.id, msg="ok")
    result.msg = "fail" if row is None else "ok"
    result.id = item_category.id
    return result   