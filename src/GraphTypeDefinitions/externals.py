import strawberry
import uuid
import typing

from uoishelpers.gqlpermissions import OnlyForAuthentized


RequestGQLModel = typing.Annotated["RequestGQLModel", strawberry.lazy(".RequestGQLModel")]

@classmethod
async def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID):
    return None if id is None else cls(id=id) 

class BaseEternal:
    id: uuid.UUID = strawberry.federation.field(external=True)
    

@strawberry.federation.type(extend=True, keys=["id"])
class UserGQLModel:
    id: uuid.UUID = strawberry.federation.field(external=True)
    resolve_reference = resolve_reference

    @strawberry.mutation(
        description="C operation",
        permission_classes=[OnlyForAuthentized])
    async def requests(self, info: strawberry.types.Info) -> typing.List[RequestGQLModel]:
        from .RequestGQLModel import RequestGQLModel
        loader = RequestGQLModel.getLoader(info=info)
        results = await loader.filter_by(createdby=self.id)
        return results
        # pass

@strawberry.federation.type(extend=True, keys=["id"])
class GroupGQLModel:
    id: uuid.UUID = strawberry.federation.field(external=True)
    resolve_reference = resolve_reference

# from utils.Dataloaders import getLoadersFromInfo
from uoishelpers.resolvers import getLoadersFromInfo
from uoishelpers.gqlpermissions import RBACObjectGQLModel

# @strawberry.federation.type(extend=True, keys=["id"])
# class RBACObjectGQLModel:
#     id: uuid.UUID = strawberry.federation.field(external=True)
#     resolve_reference = resolve_reference

#     @classmethod
#     async def resolve_roles(cls, info: strawberry.types.Info, id: uuid.UUID):
#         loader = getLoadersFromInfo(info).authorizations
#         authorizedroles = await loader.load(id)
#         return authorizedroles

@strawberry.federation.type(
    extend=True, keys=["id"]
)
class StateGQLModel():
    id: uuid.UUID = strawberry.federation.field(external=True)
    resolve_reference = resolve_reference

    @strawberry.field(description="requests associated with this state")
    async def requests(self, info: strawberry.types.Info) -> typing.List["RequestGQLModel"]:
        from .RequestGQLModel import RequestGQLModel
        loader = RequestGQLModel.getLoader(info=info)
        results = await loader.filter_by(state_id=self.id)
        return results
