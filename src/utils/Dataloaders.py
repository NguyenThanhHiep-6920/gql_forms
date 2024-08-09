from functools import cache
import logging

from src.DBDefinitions import (
    FormModel, 
    FormTypeModel, 
    FormCategoryModel,
    RequestModel, 
    HistoryModel,
    SectionModel, 
    PartModel,
    ItemModel, 
    ItemTypeModel, 
    ItemCategoryModel
)


dbmodels = {
    "forms": FormModel, 
    "formtypes": FormTypeModel, 
    "formcategories": FormCategoryModel,
    "requests": RequestModel, 
    "histories": HistoryModel,
    "sections": SectionModel, 
    "parts": PartModel,
    "items": ItemModel, 
    "itemtypes": ItemTypeModel, 
    "itemcategories": ItemCategoryModel
}

import datetime
import aiohttp
import asyncio
import os
from aiodataloader import DataLoader
from uoishelpers.resolvers import select, update, delete
from uoishelpers.dataloaders import createIdLoader


# def prepareSelect(model, where: dict):   
#     usedTables = [model.__tablename__]
#     from sqlalchemy import select, and_, or_
#     baseStatement = select(model)
#     # stmt = select(GroupTypeModel).join(GroupTypeModel.groups.property.target).filter(GroupTypeModel.groups.property.target.c.name == "22-5KB")
#     # type(GroupTypeModel.groups.property) sqlalchemy.orm.relationships.RelationshipProperty
#     # GroupTypeModel.groups.property.entity.class_
#     def limitDict(input):
#         if isinstance(input, list):
#             return [limitDict(item) for item in input]
#         if not isinstance(input, dict):
#             # print("limitDict", input)
#             return input
#         result = {key: limitDict(value) if isinstance(value, dict) else value for key, value in input.items() if value is not None}
#         return result
    
#     def convertAnd(model, name, listExpr):
#         assert len(listExpr) > 0, "atleast one attribute in And expected"
#         results = [convertAny(model, w) for w in listExpr]
#         return and_(*results)

#     def convertOr(model, name, listExpr):
#         # print("enter convertOr", listExpr)
#         assert len(listExpr) > 0, "atleast one attribute in Or expected"
#         results = [convertAny(model, w) for w in listExpr]
#         return or_(*results)

#     def convertAttributeOp(model, name, op, value):
#         # print("convertAttributeOp", type(model))
#         # print("convertAttributeOp", model, name, op, value)
#         column = getattr(model, name)
#         assert column is not None, f"cannot map {name} to model {model.__tablename__}"
#         opMethod = getattr(column, op)
#         assert opMethod is not None, f"cannot map {op} to attribute {name} of model {model.__tablename__}"
#         return opMethod(value)

#     def convertRelationship(model, attributeName, where, opName, opValue):
#         # print("convertRelationship", model, attributeName, where, opName, opValue)
#         # GroupTypeModel.groups.property.entity.class_
#         targetDBModel = getattr(model, attributeName).property.entity.class_
#         # print("target", type(targetDBModel), targetDBModel)

#         nonlocal baseStatement
#         if targetDBModel.__tablename__ not in usedTables:
#             baseStatement = baseStatement.join(targetDBModel)
#             usedTables.append(targetDBModel.__tablename__)
#         #return convertAttribute(targetDBModel, attributeName, opValue)
#         return convertAny(targetDBModel, opValue)
        
#         # stmt = select(GroupTypeModel).join(GroupTypeModel.groups.property.target).filter(GroupTypeModel.groups.property.target.c.name == "22-5KB")
#         # type(GroupTypeModel.groups.property) sqlalchemy.orm.relationships.RelationshipProperty

#     def convertAttribute(model, attributeName, where):
#         woNone = limitDict(where)
#         #print("convertAttribute", model, attributeName, woNone)
#         keys = list(woNone.keys())
#         assert len(keys) == 1, "convertAttribute: only one attribute in where expected"
#         opName = keys[0]
#         opValue = woNone[opName]

#         ops = {
#             "_eq": "__eq__",
#             "_lt": "__lt__",
#             "_le": "__le__",
#             "_gt": "__gt__",
#             "_ge": "__ge__",
#             "_in": "in_",
#             "_like": "like",
#             "_ilike": "ilike",
#             "_startswith": "startswith",
#             "_endswith": "endswith",
#         }

#         opName = ops.get(opName, None)
#         # if opName is None:
#         #     print("op", attributeName, opName, opValue)
#         #     result = convertRelationship(model, attributeName, woNone, opName, opValue)
#         # else:
#         result = convertAttributeOp(model, attributeName, opName, opValue)
#         return result
        
#     def convertAny(model, where):
        
#         woNone = limitDict(where)
#         # print("convertAny", woNone, flush=True)
#         keys = list(woNone.keys())
#         # print(keys, flush=True)
#         # print(woNone, flush=True)
#         assert len(keys) == 1, "convertAny: only one attribute in where expected"
#         key = keys[0]
#         value = woNone[key]
        
#         convertors = {
#             "_and": convertAnd,
#             "_or": convertOr
#         }
#         #print("calling", key, "convertor", value, flush=True)
#         #print("value is", value, flush=True)
#         convertor = convertors.get(key, convertAttribute)
#         convertor = convertors.get(key, None)
#         modelAttribute = getattr(model, key, None)
#         if (convertor is None) and (modelAttribute is None):
#             assert False, f"cannot recognize {model}.{key} on {woNone}"
#         if (modelAttribute is not None):
#             property = getattr(modelAttribute, "property", None)
#             target = getattr(property, "target", None)
#             # print("modelAttribute", modelAttribute, target)
#             if target is None:
#                 result = convertAttribute(model, key, value)
#             else:
#                 result = convertRelationship(model, key, where, key, value)
#         else:
#             result = convertor(model, key, value)
#         return result
    
#     filterStatement = convertAny(model, limitDict(where))
#     result = baseStatement.filter(filterStatement)
#     return result

@cache
def composeAuthUrl():
    hostname = os.environ.get("GQLUG_ENDPOINT_URL", None)
    assert hostname is not None, "undefined GQLUG_ENDPOINT_URL"
    assert "://" in hostname, "probably bad formated url, has it 'protocol' part?"
    assert "." not in hostname, "security check failed, change source code"
    return hostname

class AuthorizationLoader(DataLoader):

    query = """query($id: UUID!){result: rbacById(id: $id) {roles {user { id } group { id } roletype { id }}}}"""
            # variables = {"id": rbacobject}

    roleUrlEndpoint=None#composeAuthUrl()
    def __init__(self,
        roleUrlEndpoint=roleUrlEndpoint,
        query=query,
        demo=True):
        super().__init__(cache=True)
        self.roleUrlEndpoint = roleUrlEndpoint if roleUrlEndpoint else composeAuthUrl()
        self.query = query
        self.demo = demo
        self.authorizationToken = ""

    def setTokenByInfo(self, info):
        self.authorizationToken = ""

    async def _load(self, id):
        variables = {"id": f"{id}"}
        if self.authorizationToken != "":
            headers = {"authorization": f"Bearer {self.authorizationToken}"}
        else:
            headers = {}
        json = {
            "query": self.query,
            "variables": variables
        }
        roleUrlEndpoint=self.roleUrlEndpoint
        async with aiohttp.ClientSession() as session:
            print(f"query {roleUrlEndpoint} for json={json}")
            async with session.post(url=roleUrlEndpoint, json=json, headers=headers) as resp:
                print(resp.status)
                if resp.status != 200:
                    text = await resp.text()
                    print(text)
                    return []
                else:
                    respJson = await resp.json()

        # print(20*"respJson")
        # print(respJson)
        
        assert respJson.get("errors", None) is None, respJson["errors"]
        respdata = respJson.get("data", None)
        assert respdata is not None, "missing data response"
        result = respdata.get("result", None)
        assert result is not None, "missing result"
        roles = result.get("roles", None)
        assert roles is not None, "missing roles"
        
        # print(30*"=")
        # print(roles)
        # print(30*"=")
        return [*roles]


    async def batch_load_fn(self, keys):
        #print('batch_load_fn', keys, flush=True)
        reducedkeys = set(keys)
        awaitables = (self._load(key) for key in reducedkeys)
        results = await asyncio.gather(*awaitables)
        indexedResult = {key:result for key, result in zip(reducedkeys, results)}
        results = [indexedResult[key] for key in keys]
        return results
    
# def createIdLoader(asyncSessionMaker, dbModel) :

#     mainstmt = select(dbModel)
#     filtermethod = dbModel.id.in_
#     class Loader(DataLoader):
#         async def batch_load_fn(self, keys):
#             #print('batch_load_fn', keys, flush=True)
#             async with asyncSessionMaker() as session:
#                 statement = mainstmt.filter(filtermethod(keys))
#                 rows = await session.execute(statement)
#                 rows = rows.scalars()
#                 #return rows
#                 datamap = {}
#                 for row in rows:
#                     datamap[row.id] = row
#                 result = [datamap.get(id, None) for id in keys]
#                 return result

#         async def insert(self, entity, extraAttributes={}):
#             newdbrow = dbModel()
#             newdbrow = update(newdbrow, entity, extraAttributes)
#             async with asyncSessionMaker() as session:
#                 session.add(newdbrow)
#                 await session.commit()
#             return newdbrow

#         async def update(self, entity, extraValues={}):
#             async with asyncSessionMaker() as session:
#                 statement = mainstmt.filter_by(id=entity.id)
#                 rows = await session.execute(statement)
#                 rows = rows.scalars()
#                 rowToUpdate = next(rows, None)

#                 if rowToUpdate is None:
#                     return None

#                 dochecks = hasattr(rowToUpdate, 'lastchange')             
#                 checkpassed = True  
#                 if (dochecks):
#                     if (entity.lastchange != rowToUpdate.lastchange):
#                         result = None
#                         checkpassed = False                        
#                     else:
#                         entity.lastchange = datetime.datetime.now()
#                 if checkpassed:
#                     rowToUpdate = update(rowToUpdate, entity, extraValues=extraValues)
#                     await session.commit()
#                     result = rowToUpdate
#                     self.registerResult(result)               
#             return result

#         async def delete(self, id):
#             statement = delete(dbModel).where(dbModel.id==id)
#             async with asyncSessionMaker() as session:
#                 result = await session.execute(statement)
#                 await session.commit()
#                 self.clear(id)
#                 return result

#         def registerResult(self, result):
#             self.clear(result.id)
#             self.prime(result.id, result)
#             return result

#         def getSelectStatement(self):
#             return select(dbModel)
        
#         def getModel(self):
#             return dbModel
        
#         def getAsyncSessionMaker(self):
#             return asyncSessionMaker
        
#         async def execute_select(self, statement):
#             async with asyncSessionMaker() as session:
#                 rows = await session.execute(statement)
#                 return (
#                     self.registerResult(row)
#                     for row in rows.scalars()
#                 )
            
#         async def filter_by(self, **filters):
#             statement = mainstmt.filter_by(**filters)
#             return await self.execute_select(statement)

#         async def page(self, skip=0, limit=10, where=None, extendedfilter=None):
#             statement = mainstmt
#             if where is not None:
#                 statement = prepareSelect(dbModel, where)
#             statement = statement.offset(skip).limit(limit)
#             if extendedfilter is not None:
#                 statement = statement.filter_by(**extendedfilter)
#             logging.info(f"loader.page statement {statement}")
#             return await self.execute_select(statement)
            
#         def set_cache(self, cache_object):
#             self.cache = True
#             self._cache = cache_object

#     return Loader(cache=True)

class Loaders:
    authorizations = None
    requests = None
    histories = None
    forms = None
    formtypes = None
    formcategories = None
    sections = None
    parts = None
    items = None
    itemtypes = None
    itemcategories = None
    pass

def createLoaders(asyncSessionMaker, models=dbmodels) -> Loaders:
    class Loaders:

        @property
        @cache
        def authorizations(self):
            return AuthorizationLoader()

        @property
        @cache
        def requests(self):
            return createIdLoader(asyncSessionMaker, RequestModel)
        
        @property
        @cache
        def histories(self):
            return createIdLoader(asyncSessionMaker, HistoryModel)
        
        @property
        @cache
        def forms(self):
            return createIdLoader(asyncSessionMaker, FormModel)
        
        @property
        @cache
        def formtypes(self):
            return createIdLoader(asyncSessionMaker, FormTypeModel)
        
        @property
        @cache
        def formcategories(self):
            return createIdLoader(asyncSessionMaker, FormCategoryModel)
        
        @property
        @cache
        def sections(self):
            return createIdLoader(asyncSessionMaker, SectionModel)

        @property
        @cache
        def parts(self):
            return createIdLoader(asyncSessionMaker, PartModel)
        
        @property
        @cache
        def items(self):
            return createIdLoader(asyncSessionMaker, ItemModel)
        
        @property
        @cache
        def itemtypes(self):
            return createIdLoader(asyncSessionMaker, ItemTypeModel)

        @property
        @cache
        def itemcategories(self):
            return createIdLoader(asyncSessionMaker, ItemCategoryModel)
        
    return Loaders()


def getLoadersFromInfo(info) -> Loaders:
    context = info.context
    loaders = context["loaders"]
    return loaders

from functools import cache


demouser = {
    "id": "2d9dc5ca-a4a2-11ed-b9df-0242ac120003",
    "name": "John",
    "surname": "Newbie",
    "email": "john.newbie@world.com",
    "roles": [
        {
            "valid": True,
            "group": {
                "id": "2d9dcd22-a4a2-11ed-b9df-0242ac120003",
                "name": "Uni"
            },
            "roletype": {
                "id": "ced46aa4-3217-4fc1-b79d-f6be7d21c6b6",
                "name": "administrátor"
            }
        },
        {
            "valid": True,
            "group": {
                "id": "2d9dcd22-a4a2-11ed-b9df-0242ac120003",
                "name": "Uni"
            },
            "roletype": {
                "id": "ae3f0d74-6159-11ed-b753-0242ac120003",
                "name": "rektor"
            }
        }
    ]
}

# def getUserFromInfo(info):
#     context = info.context
#     #print(list(context.keys()))
#     user = context.get("user", None)
#     if user is None:
#         request = context.get("request", None)
#         assert request is not None, "request is missing in context :("
#         user = request.scope.get("user", None)
#         assert user is not None, "missing user in context or in request.scope"
#     logging.debug("getUserFromInfo", user)
#     return user

def getAuthorizationToken(info):
    context = info.context
    request = context.get("request", None)
    assert request is not None, "trying to get authtoken from None request"
    return request.scope["jwt"]

def getUGClient(info):
    context = info.context
    asyncClient = context.get("ug_async_gql_client", None)
    return asyncClient

def createLoadersContext(asyncSessionMaker):
    return {
        "loaders": createLoaders(asyncSessionMaker)
    }

def createUgConnectionContext(request):

    _url = os.environ.get("GQLUG_ENDPOINT_URL", None)
    token = request.scope["jwt"]
    cookies = {'authorization': token}        
    async def asyncClient(query, variables):
        payload = {"query": query, "variables": variables}
        async with aiohttp.ClientSession(cookies=cookies) as session:
            async with session.post(_url, json=payload) as resp:
                assert resp.status == 200, f"bad status ({resp.status}) during query {query} with variables {variables} to ug point ({_url}) see {resp}"
                response = await resp.json()
                return response

    from .gql_ug_proxy import get_ug_connection
    connection = get_ug_connection(request=request)
    return {
        "ug_connection": connection,
        "ug_async_gql_client": asyncClient
    }

def getUgConnection(info):
    context = info.context
    print("getUgConnection.context", context)
    connection = context.get("ug_connection", None)
    return connection