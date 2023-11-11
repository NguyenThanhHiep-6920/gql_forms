from functools import cache
import logging

from DBDefinitions import (
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

from aiodataloader import DataLoader
from uoishelpers.resolvers import select, update, delete


def prepareSelect(model, where: dict):   
    from sqlalchemy import select, and_, or_
    baseStatement = select(model)

    def limitDict(input):
        result = {key: value for key, value in input.items() if value is not None}
        return result
    
    def convertAnd(name, listExpr):
        assert len(listExpr) > 0, "atleast one attribute in And expected"
        results = [convertAny(w) for w in listExpr]
        return and_(*results)

    def convertOr(name, listExpr):
        #print("enter convertOr", listExpr)
        assert len(listExpr) > 0, "atleast one attribute in Or expected"
        results = [convertAny(w) for w in listExpr]
        return or_(*results)

    def convertAttributeOp(name, op, value):
        column = getattr(model, name)
        assert column is not None, f"cannot map {name} to model {model.__tablename__}"
        opMethod = getattr(column, op)
        assert opMethod is not None, f"cannot map {op} to attribute {name} of model {model.__tablename__}"
        return opMethod(value)

    def convertAttribute(attributeName, where):
        woNone = limitDict(where)
        #print("convertAttribute", attributeName, woNone)
        keys = list(woNone.keys())
        assert len(keys) == 1, "convertAttribute: only one attribute in where expected"
        opName = keys[0]
        opValue = woNone[opName]

        ops = {
            "_eq": "__eq__",
            "_lt": "__lt__",
            "_le": "__le__",
            "_gt": "__gt__",
            "_ge": "__ge__",
            "_in": "in_",
            "_like": "like",
            "_ilike": "ilike",
            "_startswith": "startswith",
            "_endswith": "endswith",
        }
        opName = ops[opName]
        #print("op", attributeName, opName, opValue)
        result = convertAttributeOp(attributeName, opName, opValue)
        return result
        
    def convertAny(where):
        
        woNone = limitDict(where)
        #print("convertAny", woNone, flush=True)
        keys = list(woNone.keys())
        #print(keys, flush=True)
        #print(woNone, flush=True)
        assert len(keys) == 1, "convertAny: only one attribute in where expected"
        key = keys[0]
        value = woNone[key]
        
        convertors = {
            "_and": convertAnd,
            "_or": convertOr
        }
        #print("calling", key, "convertor", value, flush=True)
        #print("value is", value, flush=True)
        convertor = convertors.get(key, convertAttribute)

        result = convertor(key, value)
        return result
    
    filterStatement = convertAny(where)
    result = baseStatement.filter(filterStatement)
    return result

class AuthLoader(DataLoader):
    query = """query()
        {
        "reps": [
            {
            "id": "13181566-afb0-11ed-9bd8-0242ac110002"
            , "__typename": "RequestGQLModel"
            }
        ]
        }    
"""
    q2 = """{
        authorizationPage {
            ... on AuthorizationGQLModel {
            id
            users {
                accesslevel
                user {
                id
                }
            }
            groups {
                accesslevel
                group {
                id
                }
            }
            roleTypes {
                accesslevel
                roleType {
                id
                }
                group {
                id
                }
            }
            }
        }
        }
"""


    async def batch_load_fn(self, keys):
        pass

def createIdLoader(asyncSessionMaker, dbModel) :

    mainstmt = select(dbModel)
    filtermethod = dbModel.id.in_
    class Loader(DataLoader):
        async def batch_load_fn(self, keys):
            #print('batch_load_fn', keys, flush=True)
            async with asyncSessionMaker() as session:
                statement = mainstmt.filter(filtermethod(keys))
                rows = await session.execute(statement)
                rows = rows.scalars()
                #return rows
                datamap = {}
                for row in rows:
                    datamap[row.id] = row
                result = [datamap.get(id, None) for id in keys]
                return result

        async def insert(self, entity, extraAttributes={}):
            newdbrow = dbModel()
            newdbrow = update(newdbrow, entity, extraAttributes)
            async with asyncSessionMaker() as session:
                session.add(newdbrow)
                await session.commit()
            return newdbrow

        async def update(self, entity, extraValues={}):
            async with asyncSessionMaker() as session:
                statement = mainstmt.filter_by(id=entity.id)
                rows = await session.execute(statement)
                rows = rows.scalars()
                rowToUpdate = next(rows, None)

                if rowToUpdate is None:
                    return None

                dochecks = hasattr(rowToUpdate, 'lastchange')             
                checkpassed = True  
                if (dochecks):
                    if (entity.lastchange != rowToUpdate.lastchange):
                        result = None
                        checkpassed = False                        
                    else:
                        entity.lastchange = datetime.datetime.now()
                if checkpassed:
                    rowToUpdate = update(rowToUpdate, entity, extraValues=extraValues)
                    await session.commit()
                    result = rowToUpdate
                    self.registerResult(result)               
            return result

        async def delete(self, id):
            statement = delete(dbModel).where(dbModel.id==id)
            async with asyncSessionMaker() as session:
                result = await session.execute(statement)
                await session.commit()
                self.clear(id)
                return result

        def registerResult(self, result):
            self.clear(result.id)
            self.prime(result.id, result)
            return result

        def getSelectStatement(self):
            return select(dbModel)
        
        def getModel(self):
            return dbModel
        
        def getAsyncSessionMaker(self):
            return asyncSessionMaker
        
        async def execute_select(self, statement):
            async with asyncSessionMaker() as session:
                rows = await session.execute(statement)
                return (
                    self.registerResult(row)
                    for row in rows.scalars()
                )
            
        async def filter_by(self, **filters):
            statement = mainstmt.filter_by(**filters)
            return await self.execute_select(statement)

        async def page(self, skip=0, limit=10, where=None, extendedfilter=None):
            statement = mainstmt
            if where is not None:
                statement = prepareSelect(dbModel, where)
            statement = statement.offset(skip).limit(limit)
            if extendedfilter is not None:
                statement = statement.filter_by(**extendedfilter)
            print(statement)
            return await self.execute_select(statement)
            
        def set_cache(self, cache_object):
            self.cache = True
            self._cache = cache_object

    return Loader(cache=True)

class Loaders:
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

def getUserFromInfo(info):
    context = info.context
    #print(list(context.keys()))
    result = context.get("user", None)
    if result is None:
        authorization = context["request"].headers.get("Authorization", None)
        if authorization is not None:
            if 'Bearer ' in authorization:
                token = authorization.split(' ')[1]
                if token == "2d9dc5ca-a4a2-11ed-b9df-0242ac120003":
                    result = demouser
                    context["user"] = result
    logging.debug("getUserFromInfo", result)
    return result

def createLoadersContext(asyncSessionMaker):
    return {
        "loaders": createLoaders(asyncSessionMaker)
    }
