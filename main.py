import os
import strawberry
import socket
import asyncio

from pydantic import BaseModel
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter
from strawberry.asgi import GraphQL

import logging
import logging.handlers

from src.GraphTypeDefinitions import schema
from src.DBDefinitions import startEngine, ComposeConnectionString
from src.utils.DBFeeder import initDB
from uoishelpers.authenticationMiddleware import createAuthentizationSentinel

# region logging setup

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s.%(msecs)03d\t%(levelname)s:\t%(message)s', 
    datefmt='%Y-%m-%dT%I:%M:%S')
SYSLOGHOST = os.getenv("SYSLOGHOST", None)
if SYSLOGHOST is not None:
    [address, strport, *_] = SYSLOGHOST.split(':')
    assert len(_) == 0, f"SYSLOGHOST {SYSLOGHOST} has unexpected structure, try `localhost:514` or similar (514 is UDP port)"
    port = int(strport)
    my_logger = logging.getLogger()
    my_logger.setLevel(logging.INFO)
    handler = logging.handlers.SysLogHandler(address=(address, port), socktype=socket.SOCK_DGRAM)
    #handler = logging.handlers.SocketHandler('10.10.11.11', 611)
    my_logger.addHandler(handler)


# endregion

# region DB setup

## Definice GraphQL typu (pomoci strawberry https://strawberry.rocks/)
## Strawberry zvoleno kvuli moznosti mit federovane GraphQL API (https://strawberry.rocks/docs/guides/federation, https://www.apollographql.com/docs/federation/)
## Definice DB typu (pomoci SQLAlchemy https://www.sqlalchemy.org/)
## SQLAlchemy zvoleno kvuli moznost komunikovat s DB asynchronne
## https://docs.sqlalchemy.org/en/14/core/future.html?highlight=select#sqlalchemy.future.select


## Zabezpecuje prvotni inicializaci DB a definovani Nahodne struktury pro "Univerzity"
# from gql_workflow.DBFeeder import createSystemDataStructureRoleTypes, createSystemDataStructureGroupTypes

connectionString = ComposeConnectionString()

def singleCall(asyncFunc):
    """Dekorator, ktery dovoli, aby dekorovana funkce byla volana (vycislena) jen jednou. Navratova hodnota je zapamatovana a pri dalsich volanich vracena.
    Dekorovana funkce je asynchronni.
    """
    resultCache = {}

    async def result():
        if resultCache.get("result", None) is None:
            resultCache["result"] = await asyncFunc()
        return resultCache["result"]

    return result

@singleCall
async def RunOnceAndReturnSessionMaker():
    """Provadi inicializaci asynchronniho db engine, inicializaci databaze a vraci asynchronni SessionMaker.
    Protoze je dekorovana, volani teto funkce se provede jen jednou a vystup se zapamatuje a vraci se pri dalsich volanich.
    """

    # makeDrop = os.getenv("DEMO", None) == "True"
    makeDrop = False
    logging.info(f'starting engine for "{connectionString} makeDrop={makeDrop}"')

    result = await startEngine(
        connectionstring=connectionString, makeDrop=makeDrop, makeUp=True
    )

    logging.info(f"initializing system structures")

    ###########################################################################################################################
    #
    # zde definujte do funkce asyncio.gather
    # vlozte asynchronni funkce, ktere maji data uvest do prvotniho konzistentniho stavu
    
    # await initDB(result)
    asyncio.create_task(initDB(result))
    #
    #
    ###########################################################################################################################
    logging.info(f"all done")
    return result

# endregion

# region Sentinel setup
JWTPUBLICKEYURL = os.environ.get("JWTPUBLICKEYURL", "http://localhost:8000/oauth/publickey")
JWTRESOLVEUSERPATHURL = os.environ.get("JWTRESOLVEUSERPATHURL", "http://localhost:8000/oauth/userinfo")

apolloQuery = "query __ApolloGetServiceDefinition__ { _service { sdl } }"
graphiQLQuery = "\n    query IntrospectionQuery {\n      __schema {\n        \n        queryType { name }\n        mutationType { name }\n        subscriptionType { name }\n        types {\n          ...FullType\n        }\n        directives {\n          name\n          description\n          \n          locations\n          args(includeDeprecated: true) {\n            ...InputValue\n          }\n        }\n      }\n    }\n\n    fragment FullType on __Type {\n      kind\n      name\n      description\n      \n      fields(includeDeprecated: true) {\n        name\n        description\n        args(includeDeprecated: true) {\n          ...InputValue\n        }\n        type {\n          ...TypeRef\n        }\n        isDeprecated\n        deprecationReason\n      }\n      inputFields(includeDeprecated: true) {\n        ...InputValue\n      }\n      interfaces {\n        ...TypeRef\n      }\n      enumValues(includeDeprecated: true) {\n        name\n        description\n        isDeprecated\n        deprecationReason\n      }\n      possibleTypes {\n        ...TypeRef\n      }\n    }\n\n    fragment InputValue on __InputValue {\n      name\n      description\n      type { ...TypeRef }\n      defaultValue\n      isDeprecated\n      deprecationReason\n    }\n\n    fragment TypeRef on __Type {\n      kind\n      name\n      ofType {\n        kind\n        name\n        ofType {\n          kind\n          name\n          ofType {\n            kind\n            name\n            ofType {\n              kind\n              name\n              ofType {\n                kind\n                name\n                ofType {\n                  kind\n                  name\n                  ofType {\n                    kind\n                    name\n                  }\n                }\n              }\n            }\n          }\n        }\n      }\n    }\n  "


sentinel = createAuthentizationSentinel(
    JWTPUBLICKEY=JWTPUBLICKEYURL,
    JWTRESOLVEUSERPATH=JWTRESOLVEUSERPATHURL,
    queriesWOAuthentization=[apolloQuery, graphiQLQuery],
    onAuthenticationError=lambda item: JSONResponse({"data": None, "errors": ["Unauthenticated", item.query, f"{item.variables}"]}, 
    status_code=401))

# endregion

# region FastAPI setup
class Item(BaseModel):
    query: str
    variables: dict = {}
    operationName: str = None

async def get_context(request: Request):
    asyncSessionMaker = await RunOnceAndReturnSessionMaker()
        
    #from src.Dataloaders import createLoadersContext, createUgConnectionContext
    from src.utils.Dataloaders import createLoadersContext
    context = createLoadersContext(asyncSessionMaker)
    i = Item(query = "")
    # i.query = ""
    # i.variables = {}
    logging.info(f"before sentinel current user is {request.scope.get('user', None)}")
    await sentinel(request, i)
    logging.info(f"after sentinel current user is {request.scope.get('user', None)}")
    # connectionContext = createUgConnectionContext(request=request)
    # result = {**context, **connectionContext}
    result = {**context}
    result["request"] = request
    result["user"] = request.scope.get("user", None)
    logging.info(f"context created {result}")
    return result

@asynccontextmanager
async def lifespan(app: FastAPI):
    initizalizedEngine = await RunOnceAndReturnSessionMaker()
    yield

app = FastAPI(lifespan=lifespan)
# app.mount("/gql", graphql_app)

from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app, metric_namespace="gql_forms").expose(app, endpoint="/metrics")

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)

@app.get("/gql")
async def graphiql(request: Request):
    return await graphql_app.render_graphql_ide(request)

@app.post("/gql")
async def apollo_gql(request: Request, item: Item):
    DEMOE = os.getenv("DEMO", None)

    sentinelResult = await sentinel(request, item)
    if DEMOE == "False":
        if sentinelResult:
            logging.info(f"sentinel test failed for query={item} \n request={request}")
            return sentinelResult
        logging.info(f"sentinel test passed for query={item}")
    else:
        request.scope["user"] = {"id": "2d9dc5ca-a4a2-11ed-b9df-0242ac120003"}
        logging.info(f"sentinel skippend because of DEMO mode for query={item} for user {request.scope['user']}")
    try:
        context = await get_context(request)
        schemaresult = await schema.execute(query=item.query, variable_values=item.variables, operation_name=item.operationName, context_value=context)
    except Exception as e:
        logging.info(f"error during schema execute {e}")
        return {"data": None, "errors": [f"{type(e).__name__}: {e}"]}
    
    # logging.info(f"schema execute result \n{schemaresult}")
    result = {"data": schemaresult.data}
    if schemaresult.errors:
        result["errors"] = [
            {
                "msg": error.message,
                "locations": error.locations,
                "path": error.path,
                "nodes": error.nodes,
                "source": error.source,
                "original_error": { "type": f"{type(error.original_error)}", "msg": f"{error.original_error}" },
                # "msg_r": f"{error}",
                "msg_e": f"{error}".split('\n')
            } for error in schemaresult.errors]
    return result

logging.info("All initialization is done")

# @app.get('/hello')
# def hello():
#    return {'hello': 'world'}

###########################################################################################################################
#
# pokud jste pripraveni testovat GQL funkcionalitu, rozsirte apollo/server.js
#
###########################################################################################################################
# endregion

# region ENV setup tests
def envAssertDefined(name, default=None):
    result = os.getenv(name, None)
    assert result is not None, f"{name} environment variable must be explicitly defined"
    return result

DEMO = envAssertDefined("DEMO", None)
GQLUG_ENDPOINT_URL = envAssertDefined("GQLUG_ENDPOINT_URL", None)
JWTPUBLICKEYURL = envAssertDefined("JWTPUBLICKEYURL", None)
JWTRESOLVEUSERPATHURL = envAssertDefined("JWTRESOLVEUSERPATHURL", None)

assert (DEMO == "True") or (DEMO == "False"), "DEMO environment variable can have only `True` or `False` values"
DEMO = DEMO == "True"

if DEMO:
    print("####################################################")
    print("#                                                  #")
    print("# RUNNING IN DEMO                                  #")
    print("#                                                  #")
    print("####################################################")

    logging.info("####################################################")
    logging.info("#                                                  #")
    logging.info("# RUNNING IN DEMO                                  #")
    logging.info("#                                                  #")
    logging.info("####################################################")
else:
    print("####################################################")
    print("#                                                  #")
    print("# RUNNING DEPLOYMENT                               #")
    print("#                                                  #")
    print("####################################################")

    logging.info("####################################################")
    logging.info("#                                                  #")
    logging.info("# RUNNING DEPLOYMENT                               #")
    logging.info("#                                                  #")
    logging.info("####################################################")    

logging.info(f"DEMO = {DEMO}")
logging.info(f"SYSLOGHOST = {SYSLOGHOST}")
logging.info(f"GQLUG_ENDPOINT_URL = {GQLUG_ENDPOINT_URL}")
logging.info(f"JWTPUBLICKEYURL = {JWTPUBLICKEYURL}")
logging.info(f"JWTRESOLVEUSERPATHURL = {JWTRESOLVEUSERPATHURL}")
# endregion