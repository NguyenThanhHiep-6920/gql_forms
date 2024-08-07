import sqlalchemy
import asyncio
import pytest

# from ..uoishelpers.uuid import UUIDColumn

from src.GraphTypeDefinitions import schema

from tests.shared import (
    prepare_demodata,
    prepare_in_memory_sqllite,
    get_demodata,
    createContext,
)

from .gqlshared import (
    createByIdTest, 
    createPageTest, 
    createResolveReferenceTest,
    createUpdateQuery,
    CreateSchemaFunction
)

test_query_user_by_id = createByIdTest(tableName="users", queryEndpoint="userById")
test_query_group_by_id = createByIdTest(tableName="groups", queryEndpoint="groupById")
test_query_grouptype_by_id = createByIdTest(
    tableName="grouptypes", queryEndpoint="groupTypeById"
)
test_query_roletype_by_id = createByIdTest(
    tableName="roletypes", queryEndpoint="roleTypeById"
)

test_query_user_page = createPageTest(tableName="users", queryEndpoint="userPage")
test_query_group_page = createPageTest(tableName="groups", queryEndpoint="groupPage")
test_query_grouptype_page = createPageTest(
    tableName="grouptypes", queryEndpoint="groupTypePage"
)
test_query_roletype_page = createPageTest(
    tableName="roletypes", queryEndpoint="roleTypePage"
)


test_reference_user = createResolveReferenceTest(tableName="users", gqltype="UserGQLModel")
test_reference_group = createResolveReferenceTest(tableName="groups", gqltype="GroupGQLModel")
test_reference_group_type = createResolveReferenceTest(tableName="grouptypes", gqltype="GroupTypeGQLModel")
test_reference_role = createResolveReferenceTest(tableName="roles", gqltype="RoleGQLModel", attributeNames=['id'])
test_reference_role_type = createResolveReferenceTest(tableName="roletypes", gqltype="RoleTypeGQLModel")
test_reference_membership = createResolveReferenceTest(tableName="memberships", gqltype="MembershipGQLModel", attributeNames=['id'])


@pytest.mark.asyncio
async def test_large_query():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()

    query = """query {
         groupById(id: "2d9dcd22-a4a2-11ed-b9df-0242ac120003") {
            id
            name
            roles {
            user {
                id
                name
                surname
                email
            }
            roletype {
                id
                name
            }
            }
            subgroups {
            id
            name
            }
            memberships {
            user {
                id
                name

                roles {
                roletype {
                    id
                    name
                }
                group {
                    id
                    name
                }
                }

                membership {
                group {
                    id
                    name
                }
                }
            }
            }
        }
        }"""


    schemaExecutor = CreateSchemaFunction()
    variable_values = {}
    resp = await schemaExecutor(query, variable_values)

    respdata = resp["data"]["groupById"]

    assert resp["errors"] is None
    assert respdata["id"] == "2d9dcd22-a4a2-11ed-b9df-0242ac120003"



# @pytest.mark.asyncio
# async def test_query_group_editor_add_member():
#     async_session_maker = await prepare_in_memory_sqllite()
#     await prepare_demodata(async_session_maker)

#     data = get_demodata()
#     table = data['groups']
#     row = table[0]
#     query = """query($id: ID!) {
#         groupById(id: $id) {
#             memberships {
#                 user { id }
#             }
#             editor{
#                 id
#             }
#             id
#         }
#         }"""

#     context_value = createContext(async_session_maker)
#     variable_values = {"id": row["id"]}
#     resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)

#     respdata = resp["data"]["groupById"]

#     assert resp["errors"] is None
#     assert respdata["id"] == row["id"]
#     memberids = list(map(lambda item: item['user']['id'], respdata["memberships"]))

#     # vlozit vsechny uzivatele, kteri nejsou cleny
#     table2 = data['users']
#     for row2 in table2:
#         if row2['id'] in memberids:
#             continue

#         query = """query($id: ID!, $userId: ID!) {
#             groupById(id: $id) {
#                 editor{
#                     id
#                     addMembership(userId: $userId) {
#                         id
#                     }
#                 }
#                 id
#             }
#             }"""

#         context_value = createContext(async_session_maker)
#         variable_values = {"id": row["id"], "userId": row2["id"]}
#         resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)

#         assert resp["errors"] is None


#     query = """query($id: ID!) {
#         groupById(id: $id) {
#             memberships {
#                 user { id }
#             }
#             id
#         }
#         }"""

#     context_value = createContext(async_session_maker)
#     variable_values = {"id": row["id"]}
#     resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)
#     assert resp["errors"] is None
#     respdata = resp["data"]["groupById"]
#     assert respdata["id"] == row["id"]

#     memberids = list(map(lambda item: item['user']['id'], respdata["memberships"]))
#     # overit, ze vsichni uzivatele jsou cleny
#     table2 = data['users']
#     for row2 in table2:
#         if row2['id'] in memberids:
#             continue
#         assert False

import datetime

# @pytest.mark.asyncio
# async def _test_query_group_editor_update():
#     async_session_maker = await prepare_in_memory_sqllite()
#     await prepare_demodata(async_session_maker)

#     data = get_demodata()
#     table = data['groups']
#     row = table[0]

#     query = """query($id: ID!) {
#         groupById(id: $id) {
#             id
#             lastchange
#         }
#         }"""

#     context_value = createContext(async_session_maker)
#     variable_values = {"id": row["id"]}
#     resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)

#     assert resp["errors"] is None
#     respdata = resp["data"]["groupById"]
#     lastchange = respdata["lastchange"]
#     print(lastchange)
#     lastchange = datetime.datetime.fromisoformat(respdata["lastchange"])
#     print(lastchange)
#     query = """query($id: ID!, $group: GroupUpdateGQLModel!) {
#         groupById(id: $id) {
#             editor{
#                 id
#                 update(group: $group) {
#                     result
#                 }
#             }
#             id
#         }
#         }"""

#     # musi selhat, je spatne razitko
#     group = {"name": "newname", "lastchange": f"{datetime.datetime.now().isoformat()}"}
#     print(1, group, flush=True)
#     context_value = createContext(async_session_maker)
#     variable_values = {"id": row["id"], "group": group}
#     resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)

#     assert resp["errors"] is None
#     respdata = resp["data"]["groupById"]
#     assert respdata["id"] == row["id"]
#     assert respdata["editor"]["id"] == row["id"]
#     respdata = respdata["editor"]
#     assert respdata["update"]["result"] == "fail"

#     # musi projit, je spravne razitko
#     group = {"name": "newname", "lastchange": f"{lastchange.isoformat()}"}
#     print(2, group, flush=True)
#     context_value = createContext(async_session_maker)
#     variable_values = {"id": row["id"], "group": group}
#     resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)

#     assert resp["errors"] is None
#     respdata = resp["data"]["groupById"]
#     assert respdata["id"] == row["id"]
#     assert respdata["editor"]["id"] == row["id"]
#     respdata = respdata["editor"]
#     assert respdata["update"]["result"] == "ok"

# @pytest.mark.asyncio
# async def test_query_group_editor_create_user():
#     async_session_maker = await prepare_in_memory_sqllite()
#     await prepare_demodata(async_session_maker)

#     data = get_demodata()
#     table = data['groups']
#     row = table[0]
#     query = """query($id: ID!, $user: UserInsertGQLModel!) {
#         groupById(id: $id) {
#             editor{
#                 id
#                 createUser(user: $user) {
#                     id
#                     name
#                     surname
#                     email
#                     valid
#                     lastchange
#                 }
#             }
#             id
#         }
#         }"""

#     newuser = {"name": "new", "surname": "user", "email": "new.user@somewhere.else", "valid": True}

#     context_value = createContext(async_session_maker)
#     variable_values = {"id": row["id"], "user": newuser}
#     resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)

#     respdata = resp["data"]["groupById"]

#     assert resp["errors"] is None
#     assert respdata["id"] == row["id"]

#     respuser = respdata["editor"]["createUser"]
#     assert respuser["name"] == newuser["name"]
#     assert respuser["surname"] == newuser["surname"]
#     assert respuser["email"] == newuser["email"]
#     assert respuser["valid"] == newuser["valid"]


# @pytest.mark.asyncio
# async def test_query_group_editor_add_role():
#     async_session_maker = await prepare_in_memory_sqllite()
#     await prepare_demodata(async_session_maker)

#     data = get_demodata()
#     table = data['groups']
#     row = table[0]
#     query = """query($id: ID!, $userId: ID!, $roletypeId: ID!) {
#         groupById(id: $id) {
#             editor{
#                 id
#                 addRole(userId: $userId, roletypeId: $roletypeId) {
#                     id
#                 }
#             }
#             id
#         }
#         }"""

#     roletype = data['roletypes'][0]
#     user = data['users'][0]
#     context_value = createContext(async_session_maker)
#     variable_values = {"id": row["id"], "userId": user['id'], "roletypeId": roletype['id']}
#     resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)

#     respdata = resp["data"]["groupById"]

#     assert resp["errors"] is None
#     assert respdata["id"] == row["id"]

#     resprole = respdata["editor"]["addRole"]


# @pytest.mark.asyncio
# async def test_query_group_editor_add_role():
#     async_session_maker = await prepare_in_memory_sqllite()
#     await prepare_demodata(async_session_maker)

#     data = get_demodata()
#     table = data['roles']
#     row = table[0]
#     query = """query($id: ID!, $roleId: ID!) {
#         groupById(id: $id) {
#             editor{
#                 id
#                 invalidateRole(roleId: $roleId) {
#                     id
#                     valid
#                 }
#             }
#             id
#         }
#         }"""

#     context_value = createContext(async_session_maker)
#     variable_values = {"id": row["group_id"], "roleId": row['id']}
#     resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)

#     respdata = resp["data"]["groupById"]

#     assert resp["errors"] is None
#     assert respdata["id"] == row["group_id"]

#     resprole = respdata["editor"]["invalidateRole"]
#     assert resprole["valid"] == False

# @pytest.mark.asyncio
# async def test_query_random_university():
#     async_session_maker = await prepare_in_memory_sqllite()
#     await prepare_demodata(async_session_maker)

#     data = get_demodata()
#     name = "U of IT"
#     query = """query($name: String!) {
#         randomUniversity(name: $name) {
#             id
#             name
#         }
#         }"""

#     context_value = createContext(async_session_maker)
#     variable_values = {"name": name}
#     resp = await schema.execute(query, context_value=context_value, variable_values=variable_values)

#     respdata = resp["data"]["randomUniversity"]

#     assert resp["errors"] is None
#     assert respdata["name"] == name

@pytest.mark.asyncio
async def test_query_group_3L():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    letters = "Uni"
    query = """query($letters: String!) {
        groupByLetters(letters: $letters) {
            id
            name
        }
        }"""

    variable_values = {"letters": letters}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    

    respdata = resp["data"]["groupByLetters"]
    for group in respdata:
        assert letters in group['name']

    assert resp["errors"] is None

@pytest.mark.asyncio
async def test_query_user_3L():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['users']
    letters = table[0]['name']
    query = """query($letters: String!) {
        userByLetters(letters: $letters) {
            id
            name
        }
        }"""


    variable_values = {"letters": letters}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    

    respdata = resp["data"]["userByLetters"]
    for user in respdata:
        assert letters in user['name']

    assert resp["errors"] is None

@pytest.mark.asyncio
async def test_user_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['users']
    row = table[0]
    id = row['id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                userById(id: $id){
                    id
                    name
                    surname
                    lastchange
                }
            }
        '''


    variable_values = {"id": id}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    lastchange = resp["data"]['userById']['lastchange']
    newname = "Michael"
    query = '''
            mutation($id: ID!, $lastchange: DateTime!, $newname: String!) {
                userUpdate(user: {
                id: $id, name: $newname,
                lastchange: $lastchange
            }){
                id
                msg
                user {
                id
                name
                surname
                lastchange
                }
            }
            }
        '''


    variable_values = {"id": id, "lastchange": lastchange, "newname": newname}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    
    print(resp, flush=True)
    #respdata = resp["data"]['_entities']
    #print(respdata, flush=True)
    #assert respdata[0]['id'] == id
    assert resp["errors"] is None
    data = resp["data"]['userUpdate']
    assert data["user"]["name"] == newname
    assert data["msg"] == "ok"

    # zmeneno lastchange, nema projit uspesne
    
    resp = await schemaExecutor(query, variable_values)
    
    
    assert resp["errors"] is None
    data = resp["data"]['userUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_user_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    newname = "user X"
    query = '''
            mutation($name: String!) {
                userInsert(user: {
                name: $name
            }){
                id
                msg
                user {
                    id
                    name
                    lastchange
                }
            }
            }
        '''


    variable_values = {"name": newname}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['userInsert']
    assert data["user"]["name"] == newname
    assert data["msg"] == "ok"

    id = data["user"]["id"] 

    query = '''
            query($id: ID!) {
                userById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''
    variable_values = {"id": id}   
    resp = await schemaExecutor(query, variable_values)
    

    assert resp["errors"] is None
    data = resp["data"]['userById']
    assert data["name"] == newname
    assert data["id"] == id
    
    pass

@pytest.mark.asyncio
async def test_group_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['groups']
    row = table[0]
    id = row['id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                groupById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    lastchange = resp["data"]['groupById']['lastchange']
    newname = "Group X"
    query = '''
            mutation($id: ID!, $lastchange: DateTime!, $newname: String!) {
                groupUpdate(group: {
                id: $id, name: $newname,
                lastchange: $lastchange
            }){
                id
                msg
                group {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"id": id, "lastchange": lastchange, "newname": newname}    
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)
    #respdata = resp["data"]['_entities']
    #print(respdata, flush=True)
    #assert respdata[0]['id'] == id
    assert resp["errors"] is None
    data = resp["data"]['groupUpdate']
    assert data["group"]["name"] == newname
    assert data["msg"] == "ok"

    # zmeneno lastchange, nema projit uspesne
    
    resp = await schemaExecutor(query, variable_values)
    
    
    assert resp["errors"] is None
    data = resp["data"]['groupUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_group_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    newname = "Group X"
    query = '''
            mutation($name: String!) {
                groupInsert(group: {
                name: $name
            }){
                id
                msg
                group {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"name": newname}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['groupInsert']
    assert data["group"]["name"] == newname
    assert data["msg"] == "ok"

    id = data["group"]["id"] 

    query = '''
            query($id: ID!) {
                groupById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}
    
    resp = await schemaExecutor(query, variable_values)

    assert resp["errors"] is None
    data = resp["data"]['groupById']
    assert data["name"] == newname
    assert data["id"] == id
    
    pass


@pytest.mark.asyncio
async def test_role_type_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['roletypes']
    row = table[0]
    id = row['id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                roleTypeById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    lastchange = resp["data"]['roleTypeById']['lastchange']
    newname = "Group Support"
    query = '''
            mutation($id: ID!, $lastchange: DateTime!, $newname: String!) {
                roleTypeUpdate(roleType: {
                id: $id, name: $newname,
                lastchange: $lastchange
            }){
                id
                msg
                roleType {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"id": id, "lastchange": lastchange, "newname": newname}
    
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)





    assert resp["errors"] is None
    data = resp["data"]['roleTypeUpdate']
    assert data["roleType"]["name"] == newname
    assert data["msg"] == "ok"

    # zmeneno lastchange, nema projit uspesne
    
    resp = await schemaExecutor(query, variable_values)
    
    assert resp["errors"] is None
    data = resp["data"]['roleTypeUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_role_type_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    newname = "Group X"
    query = '''
            mutation($name: String!) {
                roleTypeInsert(roleType: {
                name: $name
            }){
                id
                msg
                roleType {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"name": newname}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['roleTypeInsert']
    assert data["roleType"]["name"] == newname
    assert data["msg"] == "ok"

    id = data["roleType"]["id"] 

    query = '''
            query($id: ID!) {
                roleTypeById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}
    
    resp = await schemaExecutor(query, variable_values)

    assert resp["errors"] is None
    data = resp["data"]['roleTypeById']
    assert data["name"] == newname
    assert data["id"] == id
    
    pass


@pytest.mark.asyncio
async def test_role_category_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['rolecategories']
    row = table[0]
    id = row['id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                roleCategoryById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''
    
    variable_values = {"id": id}
    print(query, variable_values, flush=True)
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    assert resp["errors"] is None
    assert resp["data"] is not None

    lastchange = resp["data"]['roleCategoryById']['lastchange']
    newname = "Group Support"
    query = '''
            mutation($id: ID!, $lastchange: DateTime!, $newname: String!) {
                roleCategoryUpdate(roleCategory: {
                id: $id, name: $newname,
                lastchange: $lastchange
            }){
                id
                msg
                roleCategory {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"id": id, "lastchange": lastchange, "newname": newname}   
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)


    assert resp["errors"] is None
    data = resp["data"]['roleCategoryUpdate']
    assert data["roleCategory"]["name"] == newname
    assert data["msg"] == "ok"

    # zmeneno lastchange, nema projit uspesne
    
    resp = await schemaExecutor(query, variable_values)
    
    assert resp["errors"] is None
    data = resp["data"]['roleCategoryUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_role_category_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    newname = "Group X"
    query = '''
            mutation($name: String!) {
                roleCategoryInsert(roleCategory: {
                name: $name
            }){
                id
                msg
                roleCategory {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"name": newname}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['roleCategoryInsert']
    assert data["roleCategory"]["name"] == newname
    assert data["msg"] == "ok"

    id = data["roleCategory"]["id"] 

    query = '''
            query($id: ID!) {
                roleCategoryById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}
    
    resp = await schemaExecutor(query, variable_values)

    assert resp["errors"] is None
    data = resp["data"]['roleCategoryById']
    assert data["name"] == newname
    assert data["id"] == id
    
    pass


@pytest.mark.asyncio
async def test_group_type_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['grouptypes']
    row = table[0]
    id = row['id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                groupTypeById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}
    print(query, variable_values, flush=True)
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    assert resp["errors"] is None
    assert resp["data"] is not None

    lastchange = resp["data"]['groupTypeById']['lastchange']
    newname = "Group Support"
    query = '''
            mutation($id: ID!, $lastchange: DateTime!, $newname: String!) {
                groupTypeUpdate(groupType: {
                id: $id, name: $newname,
                lastchange: $lastchange
            }){
                id
                msg
                groupType {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"id": id, "lastchange": lastchange, "newname": newname}   
    resp = await schemaExecutor(query, variable_values)
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['groupTypeUpdate']
    assert data["groupType"]["name"] == newname
    assert data["msg"] == "ok"

    print("# zmeneno lastchange, nema projit uspesne", flush=True)
    
    resp = await schemaExecutor(query, variable_values)
    
    assert resp["errors"] is None
    data = resp["data"]['groupTypeUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_group_type_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    newname = "Group X"
    query = '''
            mutation($name: String!) {
                groupTypeInsert(groupType: {
                name: $name
            }){
                id
                msg
                groupType {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"name": newname}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['groupTypeInsert']
    assert data["groupType"]["name"] == newname
    assert data["msg"] == "ok"

    id = data["groupType"]["id"] 

    query = '''
            query($id: ID!) {
                groupTypeById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}    
    resp = await schemaExecutor(query, variable_values)

    assert resp["errors"] is None
    data = resp["data"]['groupTypeById']
    assert data["name"] == newname
    assert data["id"] == id
    
    pass

@pytest.mark.asyncio
async def test_membership_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['memberships']
    row = table[0]
    id = row['id']
    group_id = row['group_id']
    user_id = row['user_id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                groupById(id: $id){
                    memberships {
                        id
                        lastchange
                    }
                }
            }
        '''

    
    variable_values = {"id": group_id}
    print(query, variable_values, flush=True)
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    assert resp["errors"] is None
    assert resp["data"] is not None

    memberships = resp["data"]['groupById']['memberships']
    lastchange = memberships[0]['lastchange']
    query = '''
            mutation($id: ID!, $lastchange: DateTime!) {
                membershipUpdate(membership: {
                id: $id, valid: false,
                lastchange: $lastchange
            }){
                id
                msg
                membership {
                    id
                    lastchange
                    valid
                }
            }
            }
        '''

    variable_values = {"id": id, "lastchange": lastchange}   
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['membershipUpdate']
    assert data["membership"]["valid"] == False
    assert data["msg"] == "ok"

    print("# zmeneno lastchange, nema projit uspesne", flush=True)
    
    resp = await schemaExecutor(query, variable_values)
    
    assert resp["errors"] is None
    data = resp["data"]['membershipUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_membership_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['users']
    row = table[1]
    user_id = row['id']

    table = data['groups']
    row = table[1]
    group_id = row['id']

    table = data['roletypes']
    row = table[0]
    role_id = row['id']

    query = '''
            mutation($group_id: ID!, $user_id: ID!) {
                membershipInsert(membership: {
                groupId: $group_id,
                userId: $user_id
            }){
                id
                msg
                membership {
                    id
                    group { id }
                    user { id }
                    lastchange
                }
            }
            }
        '''

    variable_values = {"group_id": group_id, "user_id": user_id}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['membershipInsert']
    assert data["membership"]["group"]["id"] == group_id
    assert data["membership"]["user"]["id"] == user_id
    assert data["msg"] == "ok"
   
    pass

@pytest.mark.asyncio
async def test_role_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['roles']
    row = table[0]
    id = row['id']
    group_id = row['group_id']
    user_id = row['user_id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                groupById(id: $id){
                    roles {
                        id
                        lastchange
                    }
                }
            }
        '''

    variable_values = {"id": group_id}
    print(query, variable_values, flush=True)
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    assert resp["errors"] is None
    assert resp["data"] is not None

    roles = resp["data"]['groupById']['roles']
    role = roles[0]
    lastchange = role['lastchange']
    assert id == role['id']

    query = '''
            mutation($id: ID!, $lastchange: DateTime!) {
                roleUpdate(role: {
                id: $id, valid: false,
                lastchange: $lastchange
            }){
                id
                msg
                role {
                    id
                    lastchange
                    valid
                }
            }
            }
        '''

    variable_values = {"id": id, "lastchange": lastchange}   
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)


    assert resp["errors"] is None
    data = resp["data"]['roleUpdate']
    assert data["role"]["valid"] == False
    assert data["msg"] == "ok"

    print("# zmeneno lastchange, nema projit uspesne", flush=True)
    
    resp = await schemaExecutor(query, variable_values)
    print(resp, flush=True)
    # assert False
    assert resp["errors"] is None
    data = resp["data"]['roleUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_role_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['users']
    row = table[1]
    user_id = row['id']

    table = data['groups']
    row = table[1]
    group_id = row['id']

    table = data['roletypes']
    row = table[0]
    roletype_id = row['id']

    query = '''
            mutation($group_id: ID!, $user_id: ID!, $roletype_id: ID!) {
                roleInsert(role: {
                groupId: $group_id,
                userId: $user_id,
                roletypeId: $roletype_id
            }){
                id
                msg
                role {
                    id
                    group { id }
                    user { id }
                    roletype { id }
                    lastchange
                }
            }
            }
        '''


    variable_values = {"group_id": group_id, "user_id": user_id, "roletype_id": roletype_id}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['roleInsert']
    assert data["role"]["group"]["id"] == group_id
    assert data["role"]["user"]["id"] == user_id
    assert data["role"]["roletype"]["id"] == roletype_id
    assert data["msg"] == "ok"
   
    pass


@pytest.mark.asyncio
async def test_role_type_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['roletypes']
    row = table[0]
    id = row['id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                roleTypeById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    lastchange = resp["data"]['roleTypeById']['lastchange']
    newname = "Group Support"
    query = '''
            mutation($id: ID!, $lastchange: DateTime!, $newname: String!) {
                roleTypeUpdate(roleType: {
                id: $id, name: $newname,
                lastchange: $lastchange
            }){
                id
                msg
                roleType {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"id": id, "lastchange": lastchange, "newname": newname}
    resp = await schemaExecutor(query, variable_values)    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['roleTypeUpdate']
    assert data["roleType"]["name"] == newname
    assert data["msg"] == "ok"

    # zmeneno lastchange, nema projit uspesne
    
    resp = await schemaExecutor(query, variable_values)
    
    assert resp["errors"] is None
    data = resp["data"]['roleTypeUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_role_type_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    newname = "Group X"
    query = '''
            mutation($name: String!) {
                roleTypeInsert(roleType: {
                name: $name
            }){
                id
                msg
                roleType {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"name": newname}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['roleTypeInsert']
    assert data["roleType"]["name"] == newname
    assert data["msg"] == "ok"

    id = data["roleType"]["id"] 

    query = '''
            query($id: ID!) {
                roleTypeById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}
    
    resp = await schemaExecutor(query, variable_values)

    assert resp["errors"] is None
    data = resp["data"]['roleTypeById']
    assert data["name"] == newname
    assert data["id"] == id
    
    pass


@pytest.mark.asyncio
async def test_role_category_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['rolecategories']
    row = table[0]
    id = row['id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                roleCategoryById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}
    print(query, variable_values, flush=True)
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    assert resp["errors"] is None
    assert resp["data"] is not None

    lastchange = resp["data"]['roleCategoryById']['lastchange']
    newname = "Group Support"
    query = '''
            mutation($id: ID!, $lastchange: DateTime!, $newname: String!) {
                roleCategoryUpdate(roleCategory: {
                id: $id, name: $newname,
                lastchange: $lastchange
            }){
                id
                msg
                roleCategory {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"id": id, "lastchange": lastchange, "newname": newname}
    
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)


    assert resp["errors"] is None
    data = resp["data"]['roleCategoryUpdate']
    assert data["roleCategory"]["name"] == newname
    assert data["msg"] == "ok"

    # zmeneno lastchange, nema projit uspesne
    
    resp = await schemaExecutor(query, variable_values)
    
    assert resp["errors"] is None
    data = resp["data"]['roleCategoryUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_role_category_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    newname = "Group X"
    query = '''
            mutation($name: String!) {
                roleCategoryInsert(roleCategory: {
                name: $name
            }){
                id
                msg
                roleCategory {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"name": newname}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['roleCategoryInsert']
    assert data["roleCategory"]["name"] == newname
    assert data["msg"] == "ok"

    id = data["roleCategory"]["id"] 

    query = '''
            query($id: ID!) {
                roleCategoryById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}   
    resp = await schemaExecutor(query, variable_values)

    assert resp["errors"] is None
    data = resp["data"]['roleCategoryById']
    assert data["name"] == newname
    assert data["id"] == id
    
    pass


@pytest.mark.asyncio
async def test_group_type_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['grouptypes']
    row = table[0]
    id = row['id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                groupTypeById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}
    print(query, variable_values, flush=True)
    schemaExecutor = CreateSchemaFunction()
    assert resp["errors"] is None
    assert resp["data"] is not None

    lastchange = resp["data"]['groupTypeById']['lastchange']
    newname = "Group Support"
    query = '''
            mutation($id: ID!, $lastchange: DateTime!, $newname: String!) {
                groupTypeUpdate(groupType: {
                id: $id, name: $newname,
                lastchange: $lastchange
            }){
                id
                msg
                groupType {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"id": id, "lastchange": lastchange, "newname": newname}
    
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)


    assert resp["errors"] is None
    data = resp["data"]['groupTypeUpdate']
    assert data["groupType"]["name"] == newname
    assert data["msg"] == "ok"

    print("# zmeneno lastchange, nema projit uspesne", flush=True)
    
    resp = await schemaExecutor(query, variable_values)
    
    assert resp["errors"] is None
    data = resp["data"]['groupTypeUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_group_type_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    newname = "Group X"
    query = '''
            mutation($name: String!) {
                groupTypeInsert(groupType: {
                name: $name
            }){
                id
                msg
                groupType {
                    id
                    name
                    lastchange
                }
            }
            }
        '''

    variable_values = {"name": newname}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['groupTypeInsert']
    assert data["groupType"]["name"] == newname
    assert data["msg"] == "ok"

    id = data["groupType"]["id"] 

    query = '''
            query($id: ID!) {
                groupTypeById(id: $id){
                    id
                    name
                    lastchange
                }
            }
        '''

    variable_values = {"id": id}
    
    resp = await schemaExecutor(query, variable_values)

    assert resp["errors"] is None
    data = resp["data"]['groupTypeById']
    assert data["name"] == newname
    assert data["id"] == id
    
    pass

@pytest.mark.asyncio
async def test_membership_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['memberships']
    row = table[0]
    id = row['id']
    group_id = row['group_id']
    user_id = row['user_id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                groupById(id: $id){
                    memberships {
                        id
                        lastchange
                    }
                }
            }
        '''

    variable_values = {"id": group_id}
    print(query, variable_values, flush=True)
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    assert resp["errors"] is None
    assert resp["data"] is not None

    memberships = resp["data"]['groupById']['memberships']
    lastchange = memberships[0]['lastchange']
    query = '''
            mutation($id: ID!, $lastchange: DateTime!) {
                membershipUpdate(membership: {
                id: $id, valid: false,
                lastchange: $lastchange
            }){
                id
                msg
                membership {
                    id
                    lastchange
                    valid
                }
            }
            }
        '''

    variable_values = {"id": id, "lastchange": lastchange}
    
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)


    assert resp["errors"] is None
    data = resp["data"]['membershipUpdate']
    assert data["membership"]["valid"] == False
    assert data["msg"] == "ok"

    print("# zmeneno lastchange, nema projit uspesne", flush=True)
    
    resp = await schemaExecutor(query, variable_values)
    
    assert resp["errors"] is None
    data = resp["data"]['membershipUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_membership_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['users']
    row = table[1]
    user_id = row['id']

    table = data['groups']
    row = table[1]
    group_id = row['id']

    table = data['roletypes']
    row = table[0]
    role_id = row['id']

    query = '''
            mutation($group_id: ID!, $user_id: ID!) {
                membershipInsert(membership: {
                groupId: $group_id,
                userId: $user_id
            }){
                id
                msg
                membership {
                    id
                    group { id }
                    user { id }
                    lastchange
                }
            }
            }
        '''

    variable_values = {"group_id": group_id, "user_id": user_id}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['membershipInsert']
    assert data["membership"]["group"]["id"] == group_id
    assert data["membership"]["user"]["id"] == user_id
    assert data["msg"] == "ok"
   
    pass

@pytest.mark.asyncio
async def test_role_update():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['roles']
    row = table[0]
    id = row['id']
    group_id = row['group_id']
    user_id = row['user_id']
    
    print(id, flush=True)

    query = '''
            query($id: ID!) {
                groupById(id: $id){
                    roles {
                        id
                        lastchange
                    }
                }
            }
        '''

    
    variable_values = {"id": group_id}
    print(query, variable_values, flush=True)
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    assert resp["errors"] is None
    assert resp["data"] is not None

    roles = resp["data"]['groupById']['roles']
    role = roles[0]
    lastchange = role['lastchange']
    assert id == role['id']

    query = '''
            mutation($id: ID!, $lastchange: DateTime!) {
                roleUpdate(role: {
                id: $id, valid: false,
                lastchange: $lastchange
            }){
                id
                msg
                role {
                    id
                    lastchange
                    valid
                }
            }
            }
        '''

    variable_values = {"id": id, "lastchange": lastchange}   
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)


    assert resp["errors"] is None
    data = resp["data"]['roleUpdate']
    assert data["role"]["valid"] == False
    assert data["msg"] == "ok"

    print("# zmeneno lastchange, nema projit uspesne", flush=True)
    
    resp = await schemaExecutor(query, variable_values)
    print(resp, flush=True)
    # assert False
    assert resp["errors"] is None
    data = resp["data"]['roleUpdate']
    assert data["msg"] == "fail"

    pass

@pytest.mark.asyncio
async def test_role_insert():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    table = data['users']
    row = table[1]
    user_id = row['id']

    table = data['groups']
    row = table[1]
    group_id = row['id']

    table = data['roletypes']
    row = table[0]
    roletype_id = row['id']

    query = '''
            mutation($group_id: ID!, $user_id: ID!, $roletype_id: ID!) {
                roleInsert(role: {
                groupId: $group_id,
                userId: $user_id,
                roletypeId: $roletype_id
            }){
                id
                msg
                role {
                    id
                    group { id }
                    user { id }
                    roletype { id }
                    lastchange
                }
            }
            }
        '''

    variable_values = {"group_id": group_id, "user_id": user_id, "roletype_id": roletype_id}
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['roleInsert']
    assert data["role"]["group"]["id"] == group_id
    assert data["role"]["user"]["id"] == user_id
    assert data["role"]["roletype"]["id"] == roletype_id
    assert data["msg"] == "ok"
   
    pass


@pytest.mark.asyncio
async def test_user_mutation():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    
    name = "user X"
    query = '''
            mutation(
                $name: String!
                
                ) {
                operation: userInsert(user: {
                    name: $name
                    
                }){
                    id
                    msg
                    entity: user {
                        id
                        name
                        lastchange
                    }
                }
            }
        '''

    variable_values = {
        "name": name
    }
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['operation']
    assert data["msg"] == "ok"
    data = data["entity"]
    assert data["name"] == name
    
    #assert data["name"] == name
    
   
    id = data["id"]
    lastchange = data["lastchange"]
    name = "NewName"
    query = '''
            mutation(
                $id: ID!,
                $lastchange: DateTime!
                $name: String!
                ) {
                operation: userUpdate(user: {
                id: $id,
                lastchange: $lastchange
                name: $name
            }){
                id
                msg
                entity: user {
                    id
                    name
                    lastchange
                }
            }
            }
        '''
    newName = "newName"
    variable_values = {"id": id, "name": newName, "lastchange": lastchange}
    
    resp = await schemaExecutor(query, variable_values)
    assert resp["errors"] is None

    data = resp["data"]['operation']
    assert data['msg'] == "ok"
    data = data["entity"]
    assert data["name"] == newName

    # lastchange je jine, musi fail
    
    resp = await schemaExecutor(query, variable_values)
    assert resp["errors"] is None
    data = resp["data"]['operation']
    assert data['msg'] == "fail"

    pass


@pytest.mark.asyncio
async def test_group_mutation():
    async_session_maker = await prepare_in_memory_sqllite()
    await prepare_demodata(async_session_maker)

    data = get_demodata()
    
    table = data["groups"]
    row = table[0]
    user_id = row["id"]


    name = "group X"
    query = '''
            mutation(
                $name: String!
                
                ) {
                operation: groupInsert(group: {
                    name: $name
                    
                }){
                    id
                    msg
                    entity: group {
                        id
                        name
                        lastchange
                    }
                }
            }
        '''

    variable_values = {
        "name": name
    }
    schemaExecutor = CreateSchemaFunction()
    resp = await schemaExecutor(query, variable_values)
    
    print(resp, flush=True)

    assert resp["errors"] is None
    data = resp["data"]['operation']
    assert data["msg"] == "ok"
    data = data["entity"]
    assert data["name"] == name
    
    #assert data["name"] == name
    
   
    id = data["id"]
    lastchange = data["lastchange"]
    name = "NewName"
    query = '''
            mutation(
                $id: ID!,
                $lastchange: DateTime!
                $name: String!
                ) {
                operation: groupUpdate(group: {
                lastchange: $lastchange
                name: $name
                id: $id
            }){
                id
                msg
                entity: group {
                    name
                    id
                    lastchange
                }
            }
            }
        '''
    newName = "newName"
    variable_values = {"id": id, "name": newName, "lastchange": lastchange}
    
    resp = await schemaExecutor(query, variable_values)
    assert resp["errors"] is None

    data = resp["data"]['operation']
    assert data['msg'] == "ok"
    data = data["entity"]
    assert data["name"] == newName

    #lastchange = data["lastchange"]
    print(lastchange, flush=True)
    variable_values = {"id": id, "name": newName, "lastchange": lastchange}
    # #lastchange je jine, musi fail
    
    resp = await schemaExecutor(query, variable_values)
    assert resp["errors"] is None
    data = resp["data"]['operation']
    #assert data['msg'] == "fail"
    #assert False

    pass
