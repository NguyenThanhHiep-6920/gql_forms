# import strawberry
# import datetime
# import typing
# import uuid

# from typing import Annotated
# from uoishelpers.resolvers import getLoadersFromInfo, getUserFromInfo

# from .BaseGQLModel import BaseGQLModel

# from ._GraphPermissions import RoleBasedPermission, OnlyForAuthentized
# from ._GraphResolvers import (
#     resolve_id,
#     resolve_name,
#     resolve_name_en,
#     resolve_changedby,
#     resolve_created,
#     resolve_lastchange,
#     resolve_createdby,
#     resolve_rbacobject,
#     # createRootResolver_by_id,
#     # createRootResolver_by_page

#     encapsulateInsert,
#     encapsulateUpdate,
#     encapsulateDelete
# )

# from src.DBResolvers import DBResolvers


# @strawberry.federation.type(
#     keys=["id"], description="""Entity representing a state machine"""
# )
# class StateMachineGQLModel(BaseGQLModel):
#     """
#     """
#     @classmethod
#     def getLoader(cls, info):
#         return getLoadersFromInfo(info).StateMachineModel
    
#     id = resolve_id
#     name = resolve_name
#     changedby = resolve_changedby
#     lastchange = resolve_lastchange
#     created = resolve_created
#     createdby = resolve_createdby
#     name_en = resolve_name_en
#     rbacobject = resolve_rbacobject

#     @strawberry.field(
#         description="""Going from state""",
#         permission_classes=[OnlyForAuthentized])
#     async def states(self, info: strawberry.types.Info) -> typing.List["StateGQLModel"]:
#         loader = StateGQLModel.getLoader(info)
#         results = await loader.filter_by(statemachine_id=self.id)
#         return results


# @strawberry.federation.type(
#     keys=["id"], description="""Entity representing a state of state machine"""
# )
# class StateGQLModel(BaseGQLModel):
#     """
#     """
#     @classmethod
#     def getLoader(cls, info):
#         return getLoadersFromInfo(info).StateModel
    
#     id = resolve_id
#     name = resolve_name
#     changedby = resolve_changedby
#     lastchange = resolve_lastchange
#     created = resolve_created
#     createdby = resolve_createdby
#     name_en = resolve_name_en
#     rbacobject = resolve_rbacobject


# @strawberry.federation.type(
#     keys=["id"], description="""Entity representing an entity type"""
# )
# class StateChange(BaseGQLModel):
#     """
#     """
#     @classmethod
#     def getLoader(cls, info):
#         return getLoadersFromInfo(info).StateChangeModel
    
#     id = resolve_id
#     name = resolve_name
#     changedby = resolve_changedby
#     lastchange = resolve_lastchange
#     created = resolve_created
#     createdby = resolve_createdby
#     name_en = resolve_name_en
#     rbacobject = resolve_rbacobject

#     @strawberry.field(
#         description="""Going from state""",
#         permission_classes=[OnlyForAuthentized])
#     async def source(self, info: strawberry.types.Info) -> typing.Optional["StateGQLModel"]:
#         result = await StateGQLModel.resolve_reference(info, self.source_id)
#         return result
    
#     @strawberry.field(
#         description="""Going to state""",
#         permission_classes=[OnlyForAuthentized])
#     async def target(self, info: strawberry.types.Info) -> typing.Optional["StateGQLModel"]:
#         result = await StateGQLModel.resolve_reference(info, self.target_id)
#         return result
    
#     @strawberry.field(
#         description="""Going to state""",
#         permission_classes=[OnlyForAuthentized])
#     async def statemachine(self, info: strawberry.types.Info) -> typing.Optional["StateMachineGQLModel"]:
#         result = await StateMachineGQLModel.resolve_reference(info, self.statemachine_id)
#         return result    
    
# #############################################################
# #
# # Queries
# #
# #############################################################

# from dataclasses import dataclass
# from uoishelpers.resolvers import createInputs

# @createInputs
# @dataclass
# class StateMachineWhereFilter:
#     name: str
#     name_en: str
#     id: uuid.UUID
#     created: datetime.datetime


# @createInputs
# @dataclass
# class StateWhereFilter:
#     name: str
#     name_en: str
#     id: uuid.UUID
#     created: datetime.datetime

# @createInputs
# @dataclass
# class TypeWhereFilter:
#     name: str
#     name_en: str
#     id: uuid.UUID
#     created: datetime.datetime
#     category: CategoryWhereFilter


# type_page = strawberry.field(
#     description="",
#     permission_classes=[OnlyForAuthentized],
#     resolver=DBResolvers.TypeModel.PageResolver(GQLModel=TypeGQLModel, WhereFilterModel=TypeWhereFilter))

# type_by_id = strawberry.field(
#     description="",
#     permission_classes=[OnlyForAuthentized],
#     resolver=DBResolvers.TypeModel.ByIdResolver(GQLModel=TypeGQLModel))

# category_page = strawberry.field(
#     description="",
#     permission_classes=[OnlyForAuthentized],
#     resolver=DBResolvers.CategoryModel.PageResolver(GQLModel=CategoryGQLModel, WhereFilterModel=CategoryWhereFilter))

# categroy_by_id = strawberry.field(
#     description="",
#     permission_classes=[OnlyForAuthentized],
#     resolver=DBResolvers.CategoryModel.ByIdResolver(GQLModel=CategoryGQLModel))


# #############################################################
# #
# # Mutations
# #
# #############################################################

# @strawberry.input(description="Input structure - C operation")
# class TypeInsertGQLModel:
#     name: str = strawberry.field(description="type name")   
#     id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
#     createdby: strawberry.Private[uuid.UUID] = None 

# @strawberry.input(description="Input structure - U operation")
# class TypeUpdateGQLModel:
#     lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
#     id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")

#     name: typing.Optional[str] = strawberry.field(description="form type name", default=None)
#     changedby: strawberry.Private[uuid.UUID] = None

# @strawberry.type(description="Result of CU operations")
# class TypeResultGQLModel:
#     id: uuid.UUID = strawberry.field(description="primary key of CU operation object")
#     msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
# For update operation fail should be also stated when bad lastchange has been entered.""")

#     @strawberry.field(description="Object of CU operation, final version")
#     async def type(self, info: strawberry.types.Info) -> TypeGQLModel:
#         result = await TypeGQLModel.resolve_reference(info=info, id=self.id)
#         return result

# @strawberry.mutation(
#     description="C operation",
#     permission_classes=[OnlyForAuthentized])
# async def type_insert(self, info: strawberry.types.Info, type: TypeInsertGQLModel) -> TypeResultGQLModel:
#     return await encapsulateInsert(
#         info=info,
#         loader=TypeGQLModel.getLoader(info),
#         entity=type,
#         result=TypeResultGQLModel(id=type.id, msg="ok")
#         )

# @strawberry.mutation(
#     description="U operation",
#     permission_classes=[OnlyForAuthentized])
# async def type_update(self, info: strawberry.types.Info, type: TypeUpdateGQLModel) -> TypeResultGQLModel:
#     return await encapsulateUpdate(
#         info=info,
#         loader=TypeGQLModel.getLoader(info),
#         entity=type,
#         result=TypeResultGQLModel(id=type.id, msg="ok")
#     )

# @strawberry.mutation(
#     description="U operation",
#     permission_classes=[OnlyForAuthentized])
# async def type_delete(self, info: strawberry.types.Info, id: uuid.UUID) -> TypeResultGQLModel:
#     return await encapsulateDelete(
#         info=info,
#         loader=TypeGQLModel.getLoader(info),
#         id=id,
#         result=TypeResultGQLModel(id=id, msg="ok")
#     )

# @strawberry.input(description="Input structure - C operation")
# class CategoryInsertGQLModel:
#     name: str = strawberry.field(description="category name")   
#     id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
#     createdby: strawberry.Private[uuid.UUID] = None 

# @strawberry.input(description="Input structure - U operation")
# class CategoryUpdateGQLModel:
#     lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
#     id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")

#     name: typing.Optional[str] = strawberry.field(description="category name", default=None)
#     changedby: strawberry.Private[uuid.UUID] = None

# @strawberry.category(description="Result of CU operations")
# class CategoryResultGQLModel:
#     id: uuid.UUID = strawberry.field(description="primary key of CU operation object")
#     msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
# For update operation fail should be also stated when bad lastchange has been entered.""")

#     @strawberry.field(description="Object of CU operation, final version")
#     async def category(self, info: strawberry.types.Info) -> TypeGQLModel:
#         result = await TypeGQLModel.resolve_reference(info=info, id=self.id)
#         return result


# @strawberry.mutation(
#     description="C operation",
#     permission_classes=[OnlyForAuthentized])
# async def category_insert(self, info: strawberry.types.Info, category: CategoryInsertGQLModel) -> CategoryResultGQLModel:
#     return await encapsulateInsert(
#         info=info,
#         loader=CategoryGQLModel.getLoader(info),
#         entity=category,
#         result=CategoryResultGQLModel(id=category.id, msg="ok")
#         )

# @strawberry.mutation(
#     description="U operation",
#     permission_classes=[OnlyForAuthentized])
# async def category_update(self, info: strawberry.types.Info, category: CategoryUpdateGQLModel) -> CategoryResultGQLModel:
#     return await encapsulateUpdate(
#         info=info,
#         loader=CategoryGQLModel.getLoader(info),
#         entity=category,
#         result=CategoryResultGQLModel(id=category.id, msg="ok")
#     )

# @strawberry.mutation(
#     description="U operation",
#     permission_classes=[OnlyForAuthentized])
# async def category_delete(self, info: strawberry.types.Info, id: uuid.UUID) -> CategoryResultGQLModel:
#     return await encapsulateDelete(
#         info=info,
#         loader=CategoryGQLModel.getLoader(info),
#         id=id,
#         result=CategoryResultGQLModel(id=id, msg="ok")
#     )

