import datetime
import logging
from functools import cache

# from gql_workflow.DBDefinitions import BaseModel, UserModel, GroupModel, RoleTypeModel
# import the base model, when appolo sever ask your container for the first time, gql will ask
# next step define some resolver, how to use resolver in the file graptype
# check all data strcture in database if it have -- (work)
from src.DBDefinitions import (
    FormCategoryModel,
    FormTypeModel,
    ItemTypeModel,
    ItemCategoryModel,
    FormModel,
    HistoryModel,
    RequestModel,
    SectionModel,
    PartModel,
    ItemModel,
)

from functools import cache

import os
import json
from uoishelpers.feeders import ImportModels
import datetime
import uuid

def get_demodata():
    def datetime_parser(json_dict):
        for (key, value) in json_dict.items():
            if key in ["startdate", "enddate", "lastchange", "created"]:
                if value is None:
                    dateValueWOtzinfo = None
                else:
                    try:
                        dateValue = datetime.datetime.fromisoformat(value)
                        dateValueWOtzinfo = dateValue.replace(tzinfo=None)
                    except:
                        print("jsonconvert Error", key, value, flush=True)
                        dateValueWOtzinfo = None
                
                json_dict[key] = dateValueWOtzinfo
            
            if (key in ["id", "changedby", "createdby", "rbacobject"]) or ("_id" in key):
                
                if key == "outer_id":
                    json_dict[key] = value
                elif value not in ["", None]:
                    json_dict[key] = uuid.UUID(value)
                else:
                    print(key, value)

        return json_dict


    with open("./systemdata.json", "r", encoding="utf-8") as f:
        jsonData = json.load(f, object_hook=datetime_parser)

    return jsonData

async def initDB(asyncSessionMaker):
    print("initDB Start", flush=True)
    demoMode = os.environ.get("DEMODATA", None) in ["True", "true"]
    if demoMode:
        print("initDB Full DEMODATA", flush=True)
        dbModels = [
            FormCategoryModel,
            FormTypeModel,
            ItemCategoryModel,
            ItemTypeModel,
            FormModel,
            RequestModel,
            HistoryModel,
            SectionModel,
            PartModel,
            ItemModel
        ]
    else:
        dbModels = [
            FormCategoryModel,
            FormTypeModel,
            ItemCategoryModel,
            ItemTypeModel
            ]
        
    jsonData = get_demodata()
    await ImportModels(asyncSessionMaker, dbModels, jsonData)
    print("initDB End", flush=True)
    logging.info("data (if any) imported")
    pass