import sqlalchemy
import sys
import asyncio
import uuid

# setting path
#sys.path.append("../gql_forms")

import pytest

# from ..uoishelpers.uuid import UUIDColumn

from GraphTypeDefinitions import schema

from .shared import (
    prepare_demodata,
    prepare_in_memory_sqllite,
    get_demodata,
    createContext,
)

from .gqlshared import createByIdTest, createPageTest, createResolveReferenceTest, createFrontendQuery

test_reference_forms = createResolveReferenceTest(tableName='forms', gqltype='FormGQLModel', attributeNames=["id", "name", "lastchange", "valid", "status", "sections {id}", "creator {id}"])
test_reference_requests = createResolveReferenceTest(tableName='formrequests', gqltype='RequestGQLModel')
test_reference_formtypes = createResolveReferenceTest(tableName='formtypes', gqltype='FormTypeGQLModel', attributeNames=["id", "name", "lastchange"])
test_reference_formcategories = createResolveReferenceTest(tableName='formcategories', gqltype='FormCategoryGQLModel', attributeNames=["id", "name", "lastchange"])
test_reference_histories = createResolveReferenceTest(tableName='formhistories', gqltype='RequestHistoryGQLModel')
test_reference_sections = createResolveReferenceTest(tableName='formsections', gqltype='FormSectionGQLModel', attributeNames=["id", "name", "lastchange"])
test_reference_parts = createResolveReferenceTest(tableName='formparts', gqltype='FormPartGQLModel', attributeNames=["id", "name", "lastchange", "order", "section {id}"])
test_reference_items = createResolveReferenceTest(tableName='formitems', gqltype='FormItemGQLModel', attributeNames=["id", "name", "lastchange"])
test_reference_itemtypes = createResolveReferenceTest(tableName='formitemtypes', gqltype='FormItemTypeGQLModel')
test_reference_itemcategories = createResolveReferenceTest(tableName='formitemcategories', gqltype='FormItemCategoryGQLModel')

test_query_request_by_id = createByIdTest(tableName="formrequests", queryEndpoint="requestById")
test_query_request_page = createPageTest(tableName="formrequests", queryEndpoint="requestsPage")

test_query_form_by_id = createByIdTest(tableName="forms", queryEndpoint="formById")
test_query_form_page = createPageTest(tableName="forms", queryEndpoint="formPage")
test_query_form_type_by_id = createByIdTest(tableName="formtypes", queryEndpoint="formTypeById")
test_query_form_type_page = createPageTest(tableName="formtypes", queryEndpoint="formTypePage")
test_query_form_category_by_id = createByIdTest(tableName="formcategories", queryEndpoint="formCategoryById")
test_query_form_category_page = createPageTest(tableName="formcategories", queryEndpoint="formCategoryPage")

test_query_item_by_id = createByIdTest(tableName="formitems", queryEndpoint="itemById")

test_query_item_type_by_id = createByIdTest(tableName="formitemtypes", queryEndpoint="itemTypeById")
test_query_item_type_page = createPageTest(tableName="formitemtypes", queryEndpoint="itemTypePage")
test_query_item_category_by_id = createByIdTest(tableName="formitemcategories", queryEndpoint="itemCategoryById")
test_query_item_category_page = createPageTest(tableName="formitemcategories", queryEndpoint="itemCategoryPage")

test_resolve_request = createResolveReferenceTest('formrequests', 'RequestGQLModel', ['id', 'lastchange'])
test_resolve_section = createResolveReferenceTest('formsections', 'FormSectionGQLModel', ['id', 'lastchange'])
test_resolve_part = createResolveReferenceTest('formparts', 'FormPartGQLModel', ['id', 'lastchange', 'order'])


test_form_insert = createFrontendQuery(query="""
    mutation($id: UUID!, $name: String!) { 
        result: formInsert(form: {id: $id, name: $name}) { 
            id
            msg
            form {
                id
                name
            }
        }
    }
    """, 
    variables={"id": "ccde3a8b-81d0-4e2b-9aac-42e0eb2255b3", "name": "new form"},
    asserts=[]
)


from .gqlshared import createUpdateQuery
test_form_update = createUpdateQuery(
    query="""
        mutation($id: UUID!, $name: String!, $lastchange: DateTime!) {
            formUpdate(form: {id: $id, name: $name, lastchange: $lastchange}) {
                id
                msg
                form {
                    id
                    name
                }
            }
        }
    """,
    variables={"id": "190d578c-afb1-11ed-9bd8-0242ac110002", "name": "new name"},
    tableName="forms"
)

test_item_insert = createFrontendQuery(query="""
    mutation($id: UUID!, $name: String!, $partId: UUID!) { 
        result: formItemInsert(item: {id: $id, name: $name, partId: $partId}) { 
            id
            msg
            item {
                id
                name
            }
        }
    }
    """, 
    variables={"id": "ee40b3bf-ac51-4dbb-8f73-d5da30bf8017", "name": "new item", "partId": "52e3f2d6-afb1-11ed-9bd8-0242ac110002"},
    asserts=[]
)


test_item_update = createUpdateQuery(
    query="""
        mutation($id: UUID!, $name: String!, $lastchange: DateTime!, $value: String!) {
            formItemUpdate(item: {id: $id, name: $name, lastchange: $lastchange, value: $value}) {
                id
                msg
                item {
                    id
                    name
                    value
                    lastchange
                }
            }
        }

    """,
    variables={"id": "72a3d4b0-afb1-11ed-9bd8-0242ac110002", "name": "new name", "value": "other value"},
    tableName="formitems"
)

test_item_type_insert = createFrontendQuery(query="""
    mutation($id: UUID!, $name: String!) { 
        result: formItemTypeInsert(itemType: {id: $id, name: $name}) { 
            id
            msg
            itemType {
                id
                name
            }
        }
    }
    """, 
    variables={"id": "53365ad1-acce-4c29-b0b9-c51c67af4033", "name": "new type"},
    asserts=[]
)


test_item_type_update = createUpdateQuery(
    query="""
        mutation($id: UUID!, $name: String!, $lastchange: DateTime!) {
            formItemTypeUpdate(itemType: {id: $id, name: $name, lastchange: $lastchange}) {
                id
                msg
                itemType {
                    id
                    name
                    lastchange
                }
            }
        }

    """,
    variables={"id": "9bdb916a-afb6-11ed-9bd8-0242ac110002", "name": "new name"},
    tableName="formitemtypes"
)


test_part_insert = createFrontendQuery(query="""
    mutation($id: UUID!, $name: String!, $section_id: UUID!) { 
        result: formPartInsert(part: {id: $id, name: $name, sectionId: $section_id}) { 
            id
            msg
            part {
                id
                name
            }
        }
    }
    """, 
    variables={"id": "53365ad1-acce-4c29-b0b9-c51c67af4033", "name": "new part", "section_id": "48bbc7d4-afb1-11ed-9bd8-0242ac110002"},
    asserts=[]
)


test_part_update = createUpdateQuery(
    query="""
        mutation($id: UUID!, $name: String!, $lastchange: DateTime!) {
            formPartUpdate(part: {id: $id, name: $name, lastchange: $lastchange}) {
                id
                msg
                part {
                    id
                    name
                    lastchange
                }
            }
        }

    """,
    variables={"id": "52e3ee26-afb1-11ed-9bd8-0242ac110002", "name": "new name"},
    tableName="formparts"
)

@pytest.mark.asyncio
async def test_large_query_1():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['formrequests']
    row = table[0]
    rowid = f"{row['id']}"
    query = 'query{requestById(id: "' + rowid + '''") { 
        id
        name
        lastchange
        histories {
            request { id }
            form {
                id
                name
                nameEn
                sections {
                    id
                    name
                    order
                    form { id }
                    parts {
                        id
                        name
                        items {
                            id
                            name
                        }
                    }
                }
                type {
                    id
                    name
                    nameEn
                    category {
                        id
                        name
                        nameEn
                    }
                }

            }
        }
    }}'''

    context_value = createContext(async_session_maker)
    resp = await schema.execute(query, context_value=context_value)
    data = resp.data
    data = data['requestById']

    print(data, flush=True)
    
    assert resp.errors is None
    assert data['id'] == rowid

@pytest.mark.asyncio
async def test_request_createdby():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['formrequests']
    row = table[0]
    rowid = f"{row['id']}"
    query = 'query{requestById(id: "' + rowid + '''") { 
        id
        name
        lastchange
        creator { id }
    }}'''

    context_value = createContext(async_session_maker)
    resp = await schema.execute(query, context_value=context_value)
    data = resp.data
    data = data['requestById']

    print(data, flush=True)
    
    assert resp.errors is None
    assert data['id'] == rowid

@pytest.mark.asyncio
async def test_large_query():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['formrequests']
    row = table[0]
    user_id = row["createdby"]
    user_id = f"{user_id}"

    query = '''query($user_id: UUID!){
        result: requestsPage(where:{createdby: {_eq: $user_id}}) { 
        id
        lastchange
        creator {
            id
        }
        histories {
            id
            request { id }
            form { id }
        }
    }}'''

    context_value = createContext(async_session_maker)
    variable_values = {"user_id": user_id}
    resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
    print(resp)
    assert resp.errors is None
    data = resp.data
    data = data['result']
    data = data[0]
    #assert False
    #respdata = resp.data['eventById']
    

    assert data['creator']['id'] == user_id


@pytest.mark.asyncio
async def _test_resolve_section():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['formparts']
    row = table[0]

    query = '''
            query {
                _entities(representations: [{ __typename: "PartGQLModel", id: "''' + row['id'] +  '''" }]) {
                    ...on PartGQLModel {
                        id
                        section { id }
                        lastchange
                        order
                    }
                }
            }
        '''

    context_value = createContext(async_session_maker)
    resp = await schema.execute(query, context_value=context_value)
    data = resp.data
    print(data, flush=True)
    data = data['_entities'][0]


@pytest.mark.asyncio
async def test_resolve_item():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['formitems']
    row = table[0]
    rowid = f"{row['id']}"
    query = '''
            query($id: UUID!) {
                _entities(representations: [{ __typename: "FormItemGQLModel", id: $id }]) {
                    ...on FormItemGQLModel {
                        id
                        part { id }
                        lastchange
                        order
                        name
                        value
                        type { 
                            id
                            category { id }
                        }
                    }
                }
            }
        '''

    context_value = createContext(async_session_maker)
    variable_values = {"id": rowid}
    resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
    data = resp.data
    print(data, flush=True)
    data = data['_entities'][0]


@pytest.mark.asyncio
async def test_reference_history():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['formhistories']
    row = table[0]
    id = f'{row["id"]}'
    query = '''
            query($id: UUID!) {
                _entities(representations: [{ __typename: "RequestHistoryGQLModel", id: $id }]) {
                    ...on RequestHistoryGQLModel {
                        id
                        name
                        lastchange
                        request { id }
                        form { id }
                    }
                }
            }
        '''

    context_value = createContext(async_session_maker)
    variable_values = {'id': id}

    resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
    assert resp.errors is None
    data = resp.data
    print(data, flush=True)
    data = data['_entities'][0]
    assert data['id'] == id


@pytest.mark.asyncio
async def test_reference_user():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['users']
    row = table[0]
    id = f'{row["id"]}'
    query = '''
            query($id: UUID!) {
                _entities(representations: [{ __typename: "UserGQLModel", id: $id }]) {
                    ...on UserGQLModel {
                        id
                    }
                }
            }
        '''

    context_value = createContext(async_session_maker)
    variable_values = {'id': id}

    resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
    assert resp.errors is None
    data = resp.data
    print(data, flush=True)
    data = data['_entities'][0]
    assert data['id'] == id

    
@pytest.mark.asyncio
async def _test_requests_by_letters():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['formrequests']
    row = table[0]

    query = '''
            query($letters: String!) {
                requestsByLetters(letters: $letters) {
                    id
                }
            }
        '''

    context_value = createContext(async_session_maker)
    variable_values = {'letters': row['name'][:4]}

    resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
    assert resp.errors is None
    data = resp.data
    print(data, flush=True)
    data = data['requestsByLetters'][0]
    assert data['id'] == row['id']

@pytest.mark.asyncio
async def _test_new_request():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['formtypes']
    row = table[0]

    query = '''
            query($id: UUID!) {
                newRequest(formtypeId: $id) {
                    id
                }
            }
        '''

    context_value = createContext(async_session_maker)
    variable_values = {'id': row['id']}
    resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
    assert resp.errors is None
    data = resp.data
    print(data, flush=True)
    data = data['newRequest']

    rid = data['id']

    query = '''
            query($id: UUID!) {
                requestById(id: $id) {
                    id
                }
            }
        '''

    context_value = createContext(async_session_maker)
    variable_values = {'id': rid}
    resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
    assert resp.errors is None
    data = resp.data
    print(data, flush=True)
    assert 'requestById' in data
    data = data['requestById']
    assert data['id'] == rid

    print(data['id'], flush=True)

@pytest.mark.asyncio
async def test_say_hello_forms():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    query = '''
            query($id: UUID!) {
                sayHelloForms(id: $id)
            }
        '''

    context_value = createContext(async_session_maker)
    variable_values = {'id': '6d213a0d-2e24-4d4b-9595-90beb663a388'}
    resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
    assert resp.errors is None
    data = resp.data
    print(data, flush=True)
    data = data['sayHelloForms']
    assert 'ello' in data

@pytest.mark.asyncio
async def _test_form_mutation():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    
    table = data["forms"]
    row = table[0]
    user_id = row["id"]


    name = "form X"
    query = '''
            mutation(
                $name: String!
                
                ) {
                operation: formInsert(form: {
                    name: $name
                    
                }){
                    id
                    msg
                    entity: form {
                        id
                        name
                        lastchange
                    }
                }
            }
        '''

    context_value = createContext(async_session_maker)
    variable_values = {
        "name": name
    }
    resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
    
    print(resp, flush=True)

    assert resp.errors is None
    data = resp.data['operation']
    assert data["msg"] == "ok"
    data = data["entity"]
    assert data["name"] == name
    
    #assert data["name"] == name
    
   
    id = data["id"]
    lastchange = data["lastchange"]
    name = "NewName"
    query = '''
            mutation(
                $id: UUID!,
                $lastchange: DateTime!
                $name: String!
                ) {
                operation: formUpdate(form: {
                id: $id
                lastchange: $lastchange
                name: $name
            }){
                id
                msg
                entity: form {
                    name
                    id
                    lastchange
                }
            }
            }
        '''
    newName = "newName"
    context_value = createContext(async_session_maker)
    variable_values = {"id": id, "name": newName, "lastchange": lastchange}
    resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
    assert resp.errors is None

    data = resp.data['operation']
    assert data['msg'] == "ok"
    data = data["entity"]
    assert data["name"] == newName

    # lastchange je jine, musi fail
    resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
    assert resp.errors is None
    data = resp.data['operation']
    assert data['msg'] == "fail"

    pass
