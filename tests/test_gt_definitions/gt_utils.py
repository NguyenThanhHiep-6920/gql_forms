import pytest
import logging
import uuid
import sqlalchemy
import datetime
import os.path
import json

def checkExpected(responseJSON, expectedJSON):
    def compareLists(left, right):
        if len(left) != len(right):
            return False
        for leftValue, rightValue in zip(left, right):
            if isinstance(leftValue, dict):
                if not compareDicts(leftValue, rightValue):
                    return False
            elif isinstance(leftValue, list):
                if not compareLists(leftValue, rightValue):
                    return False
            elif leftValue != right:
                return False
        return True
            
    def compareDicts(left, right):
        allKeys = set(left.keys()).update(right.keys())
        for key in allKeys:
            leftValue = left.get(key, None)
            rightValue = right.get(key, None)
            if (leftValue is not None) and (rightValue is None):
                return False
            if (leftValue is None) and (rightValue is not None):
                return False
            if isinstance(leftValue, dict):
                if not compareDicts(leftValue, rightValue):
                    return False
            elif isinstance(leftValue, list):
                if not compareLists(leftValue, rightValue):
                    return False
            elif leftValue != rightValue:
                return False
        return True
    responseDataValue = responseJSON.get("data", None)
    expectedDataValue = expectedJSON.get("data", None)
    responseErrorValue = responseJSON.get("error", None)
    expectedErrorValue = expectedJSON.get("error", None)

    if (responseDataValue is None) and (expectedDataValue is not None):
        return False
    if (responseDataValue is not None) and (expectedDataValue is None):
        return False
    if (responseErrorValue is not None) and (expectedErrorValue is None):
        return False
    if (responseErrorValue is None) and (expectedErrorValue is not None):
        return False
    
    if not compareDicts(responseDataValue, expectedDataValue):
        return False
    if not compareDicts(responseErrorValue, expectedErrorValue):
        return False
    return True


import os 
import re
dir_path = os.path.dirname(os.path.realpath(__file__))
print("dir_path", dir_path, flush=True)

location = "./src/tests/gqls"
location = re.sub(r"\\tests\\.+", r"\\tests\\gqls", dir_path)
print("location", location, flush=True)

def getQuery(tableName, queryName):
    queryFileName = f"{location}/{tableName}/{queryName}.gql"
    with open(queryFileName, "r", encoding="utf-8") as f:
        query = f.read()
    return query

def getVariables(tableName, queryName):
    variableFileName = f"{location}/{tableName}/{queryName}.var.json"

    if os.path.isfile(variableFileName):
        with open(variableFileName, "r", encoding="utf-8") as f:
            variables = json.load(f)
    else:
        variables = {}
    return variables

def getExpectedResult(tableName, queryName):
    resultFileName = f"{location}/{tableName}/{queryName}.res.json"

    if os.path.isfile(resultFileName):
        with open(resultFileName, "r", encoding="utf-8") as f:
            expectedResult = json.load(f)
    else:
        expectedResult = None
    return expectedResult


def createByIdTest2(tableName, variables=None, expectedJson=None):
    @pytest.mark.asyncio
    async def result_test(SQLite, DemoData, ClientExecutorDemo, SchemaExecutorDemo, Env_GQLUG_ENDPOINT_URL_8124):
        # def testResult(responseJson, expectedJson):
        #     if not checkExpected(responseJson, expectedJson):
        #         assert checkExpected(responseJson, expectedJson), f"unexpected response \n{responseJson}\ninstead\n{expectedJson}"
            # print("response", responseJson)
            # errors = responseJson.get("errors", None)
            # assert errors is None, f"Error during {tableName}_by_id Execution {errors}"
            
            # respdata = responseJson.get("data", None)
            # assert respdata is not None, f"Empty response, check loader and datatable"
            # values = list(respdata.values())
            # assert len(values) > 0, f"{tableName}_by_id returns None {responseJson} as result"
            # for value in values:
            #     for attributeName, attributeValue in value.items():
            #         if attributeName in expectedJson:
            #             expectedValue = expectedJson[attributeValue]
            #             if isinstance(expectedJson, datetime.datetime):
            #                 expectedValue = expectedJson.isoformat()
            #             assert f"{value[attributeName]}" == f"{expectedValue}", f"attribute value is different {attributeName} (table {tableName})"
            #     break

        # db = DemoData
        # datarow = db[tableName][0]
        queryRead = getQuery(tableName=tableName, queryName="read")
        _variables = variables
        if _variables is None:
            _variables = getVariables(tableName=tableName, queryName="read")
        if _variables == {}:
            queryReadPage = getQuery(tableName=tableName, queryName="readp")
            pageJson = await SchemaExecutorDemo(query=queryReadPage, variable_values={})
            pageData = pageJson.get("data", None)
            assert pageData is not None, f"during query {tableName}_by_id got page result with no data {pageJson}"
            [firstKey, *_] = pageData.keys()
            # firstKey = next(pageData.keys(), None)
            assert firstKey is not None, f"during query {tableName}_by_id got empty data {pageJson}"
            rows = pageData[firstKey]
            row = rows[0]
            assert "id" in row, f"during query {tableName}_by_id got page result but rows have no ids {row}"
            _variables = row
        
        _expectedJson = expectedJson
        if _expectedJson is None:
            _expectedJson = getExpectedResult(tableName=tableName, queryName="read")
        responseJson = await SchemaExecutorDemo(query=queryRead, variable_values=_variables)
        if _expectedJson is not None:
            assert checkExpected(responseJson, _expectedJson), f"unexpected response \n{responseJson}\ninstead\n{_expectedJson}"
        else:
            logging.debug(f"query for {queryRead} with {_variables}, no tested response")
        
    return result_test

def createTest2(tableName, queryName, variables=None, expectedJson=None):
    @pytest.mark.asyncio
    async def result_test(SQLite, DemoData, ClientExecutorDemo, SchemaExecutorDemo, Env_GQLUG_ENDPOINT_URL_8124):
        query = getQuery(tableName=tableName, queryName=queryName)       
        _variables = variables
        if _variables is None:
            _variables = getVariables(tableName=tableName, queryName=queryName)       
        
        _expectedJson = expectedJson
        if _expectedJson is None:
            _expectedJson = getExpectedResult(tableName=tableName, queryName=queryName)
        responseJson = await SchemaExecutorDemo(query=query, variable_values=_variables)
        if _expectedJson is not None:
            assert checkExpected(responseJson, _expectedJson), f"unexpected response \n{responseJson}\ninstead\n{_expectedJson}"
        else:
            assert "errors" not in responseJson, f"query for {query} with {_variables}, got error {responseJson}"
            logging.debug(f"query for \n{query} with \n{_variables}, no tested response, got\n{responseJson}")
        
    return result_test

def createUpdateTest2(tableName, variables=None, expectedJson=None):
    queryName = "update"
    @pytest.mark.asyncio
    async def result_test(SQLite, DemoData, ClientExecutorDemo, SchemaExecutorDemo, Env_GQLUG_ENDPOINT_URL_8124):
        queryUpdate = getQuery(tableName=tableName, queryName=queryName)
        queryRead = getQuery(tableName=tableName, queryName="read")
        _variables = variables
        if _variables is None:
            _variables = getVariables(tableName=tableName, queryName=queryName)       

        responseJson = await SchemaExecutorDemo(query=queryRead, variable_values=_variables)
        responseData = responseJson.get("data")
        assert responseData is not None, f"got no data while asking for lastchange atribute {responseJson}"
        
        [responseEntity, *_] = responseData.values()
        assert responseEntity is not None, f"got no entity while asking for lastchange atribute {responseJson}"
        lastchange = responseEntity.get("lastchange", None)
        assert lastchange is not None, f"query read for table {tableName} is not asking for lastchange which is needed"
        _variables["lastchange"] = lastchange

        _expectedJson = expectedJson
        if _expectedJson is None:
            _expectedJson = getExpectedResult(tableName=tableName, queryName=queryName)
        responseJson = await SchemaExecutorDemo(query=queryUpdate, variable_values=_variables)
        if _expectedJson is not None:
            assert checkExpected(responseJson, expectedJson), f"unexpected response \n{responseJson}\ninstead\n{_expectedJson}"
        else:
            assert "errors" not in responseJson, f"update failed {responseJson}"
            logging.info(f"query for {queryUpdate} with {_variables}, no tested response")
        
    return result_test

def createByIdTest(tableName, queryEndpoint, attributeNames=["id", "name"]):
    @pytest.mark.asyncio
    async def result_test(SQLite, DemoData, ClientExecutorDemo, SchemaExecutorDemo, Env_GQLUG_ENDPOINT_URL_8124):
        
        def testResult(resp):
            print("response", resp)
            errors = resp.get("errors", None)
            assert errors is None, f"Error during byId Execution {errors}"
            
            respdata = resp.get("data", None)
            assert respdata is not None, f"Empty response, check loader and datatable"
            
            respdata = respdata[queryEndpoint]
            assert respdata is not None, f"{queryEndpoint} returns None {resp} as result of query for {query} with {variable_values}"

            for att in attributeNames:
                assert respdata[att] == f'{datarow[att]}'

        schemaExecutor = ClientExecutorDemo
        clientExecutor = SchemaExecutorDemo

        data = DemoData
        datarow = data[tableName][0]
        content = "{" + ", ".join(attributeNames) + "}"
        query = "query($id: UUID!){" f"{queryEndpoint}(id: $id)" f"{content}" "}"

        variable_values = {"id": f'{datarow["id"]}'}
        
        # append(queryname=f"{queryEndpoint}_{tableName}", query=query, variables=variable_values)        
        logging.debug(f"query for {query} with {variable_values}")

        resp = await schemaExecutor(query, variable_values)
        testResult(resp)
        resp = await clientExecutor(query, variable_values)
        testResult(resp)

    return result_test

def createPageTest(tableName, queryEndpoint, attributeNames=["id", "name"]):
    @pytest.mark.asyncio
    async def result_test(SQLite, DemoData, ClientExecutorDemo, SchemaExecutorDemo):

        def testResult(resp):
            errors = resp.get("errors", None)
            assert errors is None
            respdata = resp.get("data", None)
            assert respdata is not None

            respdata = respdata.get(queryEndpoint, None)
            assert respdata is not None
            datarows = data[tableName]           

            for rowa, rowb in zip(respdata, datarows):
                for att in attributeNames:
                    assert rowa[att] == f'{rowb[att]}', f"attribute `{att}` not equal {rowa[att]} != {rowb[att]}" 

        schemaExecutor = SchemaExecutorDemo
        clientExecutor = ClientExecutorDemo

        data = DemoData

        content = "{" + ", ".join(attributeNames) + "}"
        query = "query{" f"{queryEndpoint}" f"{content}" "}"

        # append(queryname=f"{queryEndpoint}_{tableName}", query=query)

        resp = await schemaExecutor(query)
        testResult(resp)
        resp = await clientExecutor(query)
        testResult(resp)
        
    return result_test

def createResolveReferenceTest(tableName, gqltype, attributeNames=["id", "name"]):
    @pytest.mark.asyncio
    async def result_test(SQLite, DemoData, ClientExecutorDemo, SchemaExecutorDemo, Context, Env_GQLUG_ENDPOINT_URL_8124):

        def testResult(resp):
            print(resp)
            errors = resp.get("errors", None)
            assert errors is None, errors
            respdata = resp.get("data", None)
            assert respdata is not None

            logging.info(respdata)
            respdata = respdata.get('_entities', None)
            assert respdata is not None

            assert len(respdata) == 1, f"got no data, is defined proper loader? test at proper table? ({tableName})"
            respdata = respdata[0]
            assert respdata is not None, f"Seems database table {tableName} is not initialized for test (conftest.py / Demodata?), also test loader"
            assert respdata['id'] == rowid, f"got id {respdata['id']} != {rowid}"

        schemaExecutor = SchemaExecutorDemo
        clientExecutor = ClientExecutorDemo

        content = "{" + ", ".join(attributeNames) + "}"

        data = DemoData
        table = data[tableName]
        for row in table:
            rowid = f"{row['id']}"

            # query = (
            #     'query($id: UUID!) { _entities(representations: [{ __typename: '+ f'"{gqltype}", id: $id' + 
            #     ' }])' +
            #     '{' +
            #     f'...on {gqltype}' + content +
            #     '}' + 
            #     '}')

            # variable_values = {"id": rowid}

            query = ("query($rep: [_Any!]!)" + 
                "{" +
                "_entities(representations: $rep)" +
                "{"+
                f"    ...on {gqltype} {content}"+
                "}"+
                "}"
            )
            
            variable_values = {"rep": [{"__typename": f"{gqltype}", "id": f"{rowid}"}]}

            logging.info(f"query representations {query} with {variable_values}")
            resp = await clientExecutor(query, {**variable_values})
            testResult(resp)
            resp = await schemaExecutor(query, {**variable_values})
            testResult(resp)

        # append(queryname=f"{gqltype}_representation", query=query)

    return result_test

def createFrontendQuery(query="{}", variables={}, asserts=[]):
    @pytest.mark.asyncio
    async def test_frontend_query(SQLite, DemoData, ClientExecutorDemo, SchemaExecutorDemo, Context, Env_GQLUG_ENDPOINT_URL_8124):    
        logging.debug("createFrontendQuery")
        # async_session_maker = await prepare_in_memory_sqllite()
        # await prepare_demodata(async_session_maker)
        # context_value = createContext(async_session_maker)
        logging.debug(f"query for {query} with {variables}")
        print(f"query for {query} with {variables}")

        # append(queryname=f"query", query=query, variables=variables)
        resp = await SchemaExecutorDemo(
            query=query, 
            variable_values=variables
        )
        # resp = await schema.execute(
        #     query=query, 
        #     variable_values=variables, 
        #     context_value=context_value
        # )

        assert resp.get("errors", None) is None, resp["errors"]
        respdata = resp.get("data", None)
        logging.info(f"query for \n{query} with \n{variables} got response: \n{respdata}")
        for a in asserts:
            a(respdata)
    return test_frontend_query


def createUpdateQuery(query="{}", variables={}, tableName=""):
    @pytest.mark.asyncio
    async def test_update(SQLite, DemoData, ClientExecutorDemo, SchemaExecutorDemo, Context, Env_GQLUG_ENDPOINT_URL_8124):
        logging.debug("test_update")
        assert variables.get("id", None) is not None, "variables has not id"
        variables["id"] = uuid.UUID(f"{variables['id']}")
        assert "$lastchange: DateTime!" in query, "query must have parameter $lastchange: DateTime!"
        assert "lastchange: $lastchange" in query, "query must use lastchange: $lastchange"
        assert tableName != "", "missing table name"

        async_session_maker = SQLite

        print("variables['id']", variables, flush=True)
        statement = sqlalchemy.text(f"SELECT id, lastchange FROM {tableName} WHERE id=:id").bindparams(id=variables['id'])
        #statement = sqlalchemy.text(f"SELECT id, lastchange FROM {tableName}")
        print("statement", statement, flush=True)
        async with async_session_maker() as session:
            rows = await session.execute(statement)
            row = rows.first()
            
            print("row", row)
            id = row[0]
            lastchange = row[1]

            print(id, lastchange)

        variables["lastchange"] = lastchange
        variables["id"] = f'{variables["id"]}'
        context_value = Context
        logging.debug(f"query for {query} with {variables}")
        print(f"query for {query} with {variables}")

        # append(queryname=f"query_{tableName}", mutation=query, variables=variables)
        resp = await SchemaExecutorDemo(
            query=query, 
            variable_values=variables
        )
        # resp = await schema.execute(
        #     query=query, 
        #     variable_values=variables, 
        #     context_value=context_value
        # )

        assert resp.get("errors", None) is None, resp["errors"]
        respdata = resp.get("data", None)
        assert respdata is not None, "GQL response is empty"
        print("respdata", respdata)
        keys = list(respdata.keys())
        assert len(keys) == 1, "expected update test has one result"
        key = keys[0]
        result = respdata.get(key, None)
        assert result is not None, f"{key} is None (test update) with {query}"
        entity = None
        for key, value in result.items():
            print(key, value, type(value))
            if isinstance(value, dict):
                entity = value
                break
        assert entity is not None, f"expected entity in response to {query}"

        for key, value in entity.items():
            if key in ["id", "lastchange"]:
                continue
            print("attribute check", type(key), f"[{key}] is {value} ?= {variables[key]}")
            assert value == variables[key], f"test on update failed {value} != {variables[key]}"

        

    return test_update