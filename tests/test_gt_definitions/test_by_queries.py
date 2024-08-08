from .gt_utils import (
    createByIdTest2,
    createUpdateTest2,
    createTest2
)


test_request_by_id = createByIdTest2(
    tableName="formrequests"
)
test_request_page = createTest2(
    tableName="formrequests",
    queryName="readp"
)
test_request_create = createTest2(
    tableName="formrequests",
    queryName="create",
    variables={
        "id": "053b5153-1683-409d-a072-0f408990c572", 
        "state_id": "eb085919-640b-43f5-863d-2e69e4a86fe4",
        "type_id": "2e1140f4-afb0-11ed-9bd8-0242ac110002",
        # "createdby": "89d1f638-ae0f-11ed-9bd8-0242ac110002",
        # "lastchange": "2023-04-19T20:00:00",
        "name": "Žádost o přerušení studia", 
        "name_en": "",
        "form_id": "190d578c-afb1-11ed-9bd8-0242ac110002"
    }
)
test_request_update = createUpdateTest2(
    tableName="formrequests",
    variables={
        "id": "13181566-afb0-11ed-9bd8-0242ac110002", 
        "name": "renamed", 
    }
)
test_request_coverage = createTest2(
    tableName="formrequests",
    queryName="coverage"
)
test_request_use_transition = createTest2(
    tableName="formrequests",
    queryName="usetransition",
    variables={
        "id": "13181566-afb0-11ed-9bd8-0242ac110002", 
        "trasition_id": "322cec6a-6c62-4611-8b67-a3b1532a9f17", 
        "lastchange": "2023-04-19T20:00:00",
        "history_message": "Vse ok"
    }
)


test_history_by_id = createByIdTest2(
    tableName="formhistories",
    variables={
        "id": "84c35266-afb5-11ed-9bd8-0242ac110002"
    }
)
test_history_insert = createTest2(
    tableName="formhistories",
    queryName="create",
    variables={
        "id": "a801c38d-40d4-4fd8-982e-43279fee4b2c",
        "request_id": "13181566-afb0-11ed-9bd8-0242ac110002", 
        "form_id": "190d578c-afb1-11ed-9bd8-0242ac110002",
        "name": "some history note"
    }
)
test_history_update = createUpdateTest2(
    tableName="formhistories",
    variables={
        "id": "84c35266-afb5-11ed-9bd8-0242ac110002",
        "name": "renamed"
    }
)

test_form_by_id = createByIdTest2(
    tableName="forms"
)
test_form_page = createTest2(
    tableName="forms",
    queryName="readp"
)
test_form_insert = createTest2(
    tableName="forms",
    queryName="create",
    variables={
        "id": "caf75323-b52f-4e10-bff7-d16368dddbc2",
        "type_id": "2e1140f4-afb0-11ed-9bd8-0242ac110002",
        "name": "Žádost", 
        "name_en": ""
    }
)
test_form_update = createUpdateTest2(
    tableName="forms",
    variables={
        "id": "190d578c-afb1-11ed-9bd8-0242ac110002",
        "name": "renamed", 
        
    }
)

test_form_coverage = createTest2(
    tableName="forms",
    queryName="coverage"
)

test_formtype_by_id = createByIdTest2(
    tableName="formtypes"
)
test_formtype_insert = createTest2(
    tableName="formtypes",
    queryName="create",
    variables={
        "id": "44060c8f-0b13-4195-baab-2b76fe00b6ad",
        "name": "new type"
    }
)
test_formtype_update = createUpdateTest2(
    tableName="formtypes",
    variables={
        "id": "2e1140f4-afb0-11ed-9bd8-0242ac110002",
        "name": "renamed type"
    }
)
test_formtype_coverage = createTest2(
    tableName="formtypes",
    queryName="coverage"
)

test_formcategory_by_id = createByIdTest2(
    tableName="formcategories"
)
test_formcategory_insert = createTest2(
    tableName="formcategories",
    queryName="create",
    variables={
        "id": "c0e90b77-f87f-43f8-baa2-e669dfe65f4f",
        "name": "new category"
    }
)
test_formcategory_update = createUpdateTest2(
    tableName="formcategories",
    variables={
        "id": "37675bd4-afb0-11ed-9bd8-0242ac110002",
        "name": "renamed category"
    }
)
test_formcategory_coverage = createTest2(
    tableName="formcategories",
    queryName="coverage"
)

test_section_by_id = createByIdTest2(
    tableName="formsections",
    variables={
        "id": "48bbc7d4-afb1-11ed-9bd8-0242ac110002"
    }
)
test_section_insert = createTest2(
    tableName="formsections",
    queryName="create",
    variables={
        "id": "c2d868d6-6523-4728-a46d-32a59bdaa5da", 
        "form_id": "190d578c-afb1-11ed-9bd8-0242ac110002", 
        "order": 1, "name": "Student", "name_en": "Student" 
    }
)
test_section_update = createUpdateTest2(
    tableName="formsections",
    variables={
        "id": "48bbc7d4-afb1-11ed-9bd8-0242ac110002", 
        "name": "renamed"
    }
)

test_part_by_id = createByIdTest2(
    tableName="formparts",
    variables={
        "id": "52e3ee26-afb1-11ed-9bd8-0242ac110002"
    }
)
test_part_insert = createTest2(
    tableName="formparts",
    queryName="create",
    variables={
        "id": "3e1b1ad3-c611-43f8-bc45-feca9f1ef775", 
        "section_id": "48bbc7d4-afb1-11ed-9bd8-0242ac110002", 
        "order": 1, "name": "Identifikace", "name_en": "Identification"
    }
)
test_part_update = createUpdateTest2(
    tableName="formparts",
    variables={
        "id": "52e3ee26-afb1-11ed-9bd8-0242ac110002", 
        "name": "renamed"
    }
)


test_item_by_id = createByIdTest2(
    tableName="formitems",
    variables={
        "id": "72a3d4b0-afb1-11ed-9bd8-0242ac110002"
    }
)
test_item_page = createTest2(
    tableName="formitems",
    queryName="readp",
)
test_item_create = createTest2(
    tableName="formitems",
    queryName="create",
    variables={
        "id": "86852021-942b-475e-9af4-24e1d11999b0", 
        "part_id": "52e3ee26-afb1-11ed-9bd8-0242ac110002",
        "type_id": "9bdb916a-afb6-11ed-9bd8-0242ac110002",
        "lastchange": "2023-04-19T20:00:00",
        "order": 1, "name": "user_id", "value": "89d1f638-ae0f-11ed-9bd8-0242ac110002", "name_en": "user_id" 
    }
)
test_item_update = createUpdateTest2(
    tableName="formitems",
    variables={
        "id": "72a3d4b0-afb1-11ed-9bd8-0242ac110002", 
        "name": "renamed"
    }
)

test_formitemtype_by_id = createByIdTest2(
    tableName="formitemtypes"
)
test_formitemtype_insert = createTest2(
    tableName="formitemtypes",
    queryName="create",
    variables={
        "id": "2605ed6d-decb-41fa-a84d-a19b108d2523",
        "name": "new item type"
    }
)
test_formitemtype_update = createUpdateTest2(
    tableName="formitemtypes",
    variables={
        "id": "9bdb916a-afb6-11ed-9bd8-0242ac110002",
        "name": "renamed item type"
    }
)

test_formitemcategory_by_id = createByIdTest2(
    tableName="formitemcategories"
)
test_formitemcategory_insert = createTest2(
    tableName="formitemcategories",
    queryName="create",
    variables={
        "id": "fd2fa9ac-3c76-4883-b499-6e440adc6310",
        "name": "new item category"
    }
)
test_formitemcategory_update = createUpdateTest2(
    tableName="formitemcategories",
    variables={
        "id": "b1cb0f80-afb8-11ed-9bd8-0242ac110002",
        "name": "renamed item category"
    }
)
test_formitemcategory_coverage = createTest2(
    tableName="formitemcategories",
    queryName="coverage",
)
