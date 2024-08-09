import strawberry
import uuid
import datetime
import typing
import logging

from .BaseGQLModel import IDType

UserGQLModel = typing.Annotated["UserGQLModel", strawberry.lazy(".externals")]
GroupGQLModel = typing.Annotated["GroupGQLModel", strawberry.lazy(".externals")]

@strawberry.field(description="""Entity primary key""")
def resolve_id(self) -> IDType:
    return self.id

@strawberry.field(description="""Name """)
def resolve_name(self) -> str:
    return self.name

@strawberry.field(description="""English name""")
def resolve_name_en(self) -> str:
    result = self.name_en if self.name_en else ""
    return result

@strawberry.field(description="""Time of last update""")
def resolve_lastchange(self) -> datetime.datetime:
    return self.lastchange

@strawberry.field(description="""Time of entity introduction""")
def resolve_created(self) -> typing.Optional[datetime.datetime]:
    return self.created

async def resolve_user(info, user_id):
    from .externals import UserGQLModel
    result = None if user_id is None else await UserGQLModel.resolve_reference(info, user_id)
    return result
    
@strawberry.field(description="""Who created entity""")
async def resolve_createdby(self, info: strawberry.types.Info) -> typing.Optional["UserGQLModel"]:
    return await resolve_user(info, self.createdby)

@strawberry.field(description="""Who made last change""")
async def resolve_changedby(self, info: strawberry.types.Info) -> typing.Optional["UserGQLModel"]:
    return await resolve_user(info, self.changedby)

RBACObjectGQLModel = typing.Annotated["RBACObjectGQLModel", strawberry.lazy(".externals")]
@strawberry.field(description="""Who made last change""")
async def resolve_rbacobject(self, info: strawberry.types.Info) -> typing.Optional[RBACObjectGQLModel]:
    from .externals import RBACObjectGQLModel
    result = None if self.rbacobject is None else await RBACObjectGQLModel.resolve_reference(info, self.rbacobject)
    return result

resolve_result_id: IDType = strawberry.field(description="primary key of CU operation object")
resolve_result_msg: str = strawberry.field(description="""Should be `ok` if descired state has been reached, otherwise `fail`.
For update operation fail should be also stated when bad lastchange has been entered.""")

# def getUserFromInfo(info: strawberry.types.Info):
#     result = info.context.get("user", None)
#     if result is None:
#         request = info.context.get("request", None)
#         assert request is not None, "request should be in context, something is wrong"
#         result = request.scope.get("user", None)
#     assert result is not None, "User is wanted but not present in context or in request.scope, check it"
#     return result

from uoishelpers.resolvers import (
    getLoadersFromInfo, 
    getUserFromInfo, 
    encapsulateDelete, 
    encapsulateInsert, 
    encapsulateUpdate
    )

# async def encapsulateInsert(info, loader, entity, result):
#     actinguser = getUserFromInfo(info)
#     id = uuid.UUID(actinguser["id"])
#     entity.createdby = id

#     row = await loader.insert(entity)
#     assert result.msg is not None, "result msg must be predefined (Operation Insert)"
#     result.id = row.id
#     return result

# async def encapsulateUpdate(info, loader, entity, result):
#     actinguser = getUserFromInfo(info)
#     id = uuid.UUID(actinguser["id"])
#     entity.changedby = id

#     row = await loader.update(entity)
#     result.id = entity.id if result.id is None else result.id 
#     result.msg = "ok" if row is not None else "fail"
#     return result

# import sqlalchemy.exc

# async def encapsulateDelete(info, loader, id, result):
#     # try:
#     #     await loader.delete(id)
#     # except sqlalchemy.exc.IntegrityError as e:
#     #     result.msg='fail'
#     # return result
#     await loader.delete(id)
#     return result