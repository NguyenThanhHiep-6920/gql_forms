# import time
# import logging
# import datetime
# import pytest_asyncio
# import uuid


# from .gt_utils import getQuery

# queries = {
#     "eventtypes": {
#         "read": """query($id: UUID!){ result: eventTypeById(id: $id) { id } }""",
#         "readext": """query($id: UUID!){ 
#             result: eventTypeById(id: $id) { 
#                 id 
#                 events { id }
#             }
#         }""",
#         "readp": """query($skip: Int, $limit: Int){ result: eventTypePage(skip: $skip, limit: $limit) { id } }""",
#         "create": """mutation ($id: UUID!, $name: String!, $name_en: String) {
#             result: eventTypeInsert(
#             eventType: {
#                 id: $id, name: $name, nameEn: $name_en, 
#             }) {
#             id
#             msg
#             result: eventType {
#                 id
#                 name
#                 events { id }
#             }
#         }
#     }"""
#     }, 
#     "eventinvitationtypes": {
#         "read": """query($id: UUID!){ result: eventInvitationTypeById(id: $id) { id } }""",
#         "readext": """query($id: UUID!){ result: eventInvitationTypeById(id: $id) { id } }""",
#         "readp": """query($skip: Int, $limit: Int){ result: eventInvitationTypePage(skip: $skip, limit: $limit) { id } }""",
#         "create": """mutation ($id: UUID!, $name: String!, $name_en: String) {
#             result: eventInvitationTypeInsert(
#             invitationType: {
#                 id: $id, name: $name, nameEn: $name_en, 
#             }) {
#             id
#             msg
#             result: invitationType {
#                 id
#                 name
#             }
#         }
#     }"""
#     },     
#     "eventpresencetypes": {
#         "read": """query($id: UUID!){ result: eventPresenceTypeById(id: $id) { id } }""",
#         "readext": """query($id: UUID!){ result: eventPresenceTypeById(id: $id) { id } }""",
#         "readp": """query($skip: Int, $limit: Int){ result: eventPresenceTypePage(skip: $skip, limit: $limit) { id } }""",
#         "create": """mutation ($id: UUID!, $name: String!, $name_en: String) {
#             result: eventPresenceTypeInsert(
#             presenceType: {
#                 id: $id, name: $name, nameEn: $name_en, 
#             }) {
#             id
#             msg
#             result: presenceType {
#                 id
#                 name
#             }
#         }
#     }"""
#     },         
#     "events": {
#         "read": """query($id: UUID!){ result: eventById(id: $id) { id } }""",
#         "readext": """query($id: UUID!){ 
#             result: eventById(id: $id) {
#                 id 
#                 description
#                 place
#                 placeId
#                 groups { id }
#             } 
#         }""",
#         "readp": """query($skip: Int, $limit: Int){ result: eventPage(skip: $skip, limit: $limit) { id } }""",
#         "create": """mutation ($id: UUID!, $startdate: DateTime!, $enddate: DateTime!,
#             $masterevent_id: UUID, $type_id: UUID!, $name: String!
#         ) {
#         result: eventInsert(event: {
#                 id: $id, name: $name,
#                 startdate: $startdate, enddate: $enddate, 
#                 mastereventId: $masterevent_id, typeId: $type_id
#             }) {
#             id
#             msg
#             result: event {
#                 id
#                 lastchange
#                 startdate enddate
#                 name
#                 presences { id }
#                 eventType { id }
#                 masterEvent { id }
#                 subEvents { id }
#             }
#         }
#     }"""        
#     },

#     "events_groups": {
#         "read": """query($id: UUID!){ result: eventPresenceById(id: $id) { id } }""",
#         "readext": """query($id: UUID!){ result: eventPresenceById(id: $id) { id } }""",
#         "readp": """query($skip: Int, $limit: Int){ result: eventPresencePage(skip: $skip, limit: $limit) { id } }""",
#         "create": """mutation (
#             $event_id: UUID!, $group_id: UUID!
#             ) {
#         result: eventGroupInsert(eventGroup: 
#             {
#                 eventId: $event_id, groupId: $group_id
#             }) {
#             id
#             msg
#             result: event {
#                 id
#             }
#         }
#     }"""
#     },

#     "events_users": {
#         "read": """query($id: UUID!){ result: eventPresenceById(id: $id) { id } }""",
#         "readext": """query($id: UUID!){ result: eventPresenceById(id: $id) { id } }""",
#         "readp": """query($skip: Int, $limit: Int){ result: eventPresencePage(skip: $skip, limit: $limit) { id } }""",
#         "create": """mutation (
#             $id: UUID, $user_id: UUID!, $event_id: UUID!, $invitationtype_id: UUID!
#             ) {
#         result: eventUserInsert(eventUser: 
#             {
#                 id: $id, userId: $user_id, eventId: $event_id, invitationtypeId: $invitationtype_id
#             }) {
#             id
#             msg
#             result: event {
#                 id lastchange
#                 presences {
#                     presenceType { id }
#                     invitationType { id }
#                     user { id }
#                     event { id }
#                 }
#             }
#         }
#     }"""
#     },                    

# }

# @pytest_asyncio.fixture
# async def GQLInsertQueries(DBModels):  
#     queries = {}
#     for DBModel in DBModels:
#         tablename = DBModel.__tablename__
#         queryset = {"read": "", "ext": "", "create": ""}
#         queries[tablename] = queryset
#         queryRead = getQuery(tableName=tablename, queryName="read")
#         queryCreate = getQuery(tableName=tablename, queryName="create")
#         queryset["read"] = queryRead
#         queryset["readext"] = queryRead
#         queryset["create"] = queryCreate

#     return queries


# @pytest_asyncio.fixture
# async def FillDataViaGQL(DBModels, DemoData, GQLInsertQueries, ClientExecutorAdmin):

#     start_time = time.time()
#     queriesR = 0
#     queriesW = 0
    

#     types = [type(""), type(datetime.datetime.now()), type(uuid.uuid1())]
#     for DBModel in DBModels:
#         tablename = DBModel.__tablename__
#         queryset = GQLInsertQueries.get(tablename, None)
#         assert queryset is not None, f"missing queries for table {tablename}"
#         table = DemoData.get(tablename, None)
#         assert table is not None, f"{tablename} is missing in DemoData"

#         readQuery = queryset.get("readext", None)
#         assert readQuery is not None, f"missing read op on table {tablename}"
#         createQuery = queryset.get("create", None)
#         assert createQuery is not None, f"missing create op on table {tablename}"

#         for row in table:
#             variable_values = {}
#             for key, value in row.items():
#                 variable_values[key] = value
#                 if isinstance(value, datetime.datetime):
#                     variable_values[key] = value.isoformat()
#                 elif type(value) in types:
#                     variable_values[key] = f"{value}"

#             # readResponse = await ClientExecutorAdmin(query=queryset["read"], variable_values=variable_values)
#             readResponse = await ClientExecutorAdmin(query=readQuery, variable_values=variable_values)
#             queriesR = queriesR + 1
#             if readResponse["data"]["result"] is not None:
#                 logging.info(f"row with id `{variable_values['id']}` already exists in `{tablename}`")
#                 continue
#             insertResponse = await ClientExecutorAdmin(query=queryset["create"], variable_values=variable_values)
#             assert insertResponse.get("errors", None) is None, insertResponse
#             queriesW = queriesW + 1

#         logging.info(f"{tablename} initialized via gql query")
#     duration = time.time() - start_time
#     logging.info(f"All WANTED tables are initialized in {duration}, total read queries {queriesR} and write queries {queriesW}")