import strawberry
import datetime
import typing
import uuid

# from utils.Dataloaders import getLoadersFromInfo, getUserFromInfo
from uoishelpers.resolvers import getLoadersFromInfo, getUserFromInfo

from .BaseGQLModel import BaseGQLModel
from ._GraphPermissions import OnlyForAuthentized
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
    # asPage
)

FormTypeGQLModel = typing.Annotated["FormTypeGQLModel", strawberry.lazy(".FormTypeGQLModel")]

@strawberry.federation.type(
    keys=["id"], description="""Entity representing a category of form types"""
)
class FormCategoryGQLModel(BaseGQLModel):
    """
    """
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).formcategories
    
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
        description="",
        permission_classes=[OnlyForAuthentized])
    async def form_types(self, info: strawberry.types.Info) -> typing.List[FormTypeGQLModel]:
        loader = getLoadersFromInfo(info).formtypes
        rows = await loader.filter_by(category_id=self.id)
        return rows

#############################################################
#
# Queries
#
#############################################################

from dataclasses import dataclass
from uoishelpers.resolvers import createInputs

@createInputs
@dataclass
class FormCategoryWhereFilter:
    name: str
    name_en: str

from src.DBResolvers import FormCategoryResolvers
@strawberry.field(
    description=""
)
async def form_category_by_id(self, info: strawberry.types.Info, id: uuid.UUID) -> typing.Optional["FormCategoryGQLModel"]:
    result = await FormCategoryGQLModel.resolve_reference(info=info, id=id)
    return result

# form_category_by_id = createRootResolver_by_id(
#     FormCategoryGQLModel, 
#     description="Retrieves the form category")

# @strawberry.field(description="Retrieves the form category")
# async def form_category_by_id(
#     self, info: strawberry.types.Info, id: uuid.UUID
# ) -> typing.Union[FormCategoryGQLModel, None]:
#     result = await FormCategoryGQLModel.resolve_reference(info=info, id=id)
#     return result


# @strawberry.field(description="Retrieves the form categories")
# async def form_category_page(
#     self, info: strawberry.types.Info, skip: int = 0, limit: int = 10,
#     where: typing.Optional[FormCategoryWhereFilter] = None
# ) -> typing.List[FormCategoryGQLModel]:
#     wf = None if where is None else strawberry.asdict(where)
#     loader = getLoadersFromInfo(info).formcategories
#     result = await loader.page(skip=skip, limit=limit, where=wf)
#     return result

form_category_page = strawberry.field(
    description='Retrieves the form categories',
        resolver=FormCategoryResolvers.Page(
        GQLModel=FormCategoryGQLModel,
        WhereFilterModel=FormCategoryWhereFilter
        )
)

#############################################################
#
# Mutations
#
#############################################################
from ._GraphPermissions import OnlyForAuthentized
@strawberry.input(description="Input structure - C operation")
class FormCategoryInsertGQLModel:
    name: str = strawberry.field(description="Category name")
    
    name_en: typing.Optional[str] = strawberry.field(description="category english name", default=None)
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    createdby: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Input structure - U Operation")
class FormCategoryUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")

    name: typing.Optional[str] = strawberry.field(description="category name", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="category english name", default=None)
    changedby: strawberry.Private[uuid.UUID] = None


from ._GraphResolvers import resolve_result_id, resolve_result_msg
@strawberry.type(
    description="Result of CU operations on FormCategory")
class FormCategoryResultGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key of CU operation object")
    msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
For update operation fail should be also stated when bad lastchange has been entered.""")
    
    msg = resolve_result_msg

    @strawberry.field(description="subject of operation")
    async def category(self, info: strawberry.types.Info) -> FormCategoryGQLModel:
        return await FormCategoryGQLModel.resolve_reference(info, self.id)


@strawberry.mutation(
    description="Create a new category",
    permission_classes=[OnlyForAuthentized])
async def form_category_insert(self, info: strawberry.types.Info, form_category: FormCategoryInsertGQLModel) -> FormCategoryResultGQLModel:
    user = getUserFromInfo(info)
    form_category.createdby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).formcategories
    row = await loader.insert(form_category)
    result = FormCategoryResultGQLModel(id=row.id, msg="ok")
    result.msg = "ok"
    result.id = row.id
    return result

@strawberry.mutation(
    description="Update the category",
    permission_classes=[OnlyForAuthentized])
async def form_category_update(self, info: strawberry.types.Info, form_category: FormCategoryUpdateGQLModel) -> FormCategoryResultGQLModel:
    user = getUserFromInfo(info)
    form_category.changedby = uuid.UUID(user["id"])
    loader = getLoadersFromInfo(info).formcategories
    row = await loader.update(form_category)
    result = FormCategoryResultGQLModel(id=form_category.id, msg="ok")
    result.msg = "fail" if row is None else "ok"
    result.id = form_category.id
    return result   
