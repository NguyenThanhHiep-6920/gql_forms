from typing import List, Union
import typing
import strawberry
import uuid
from contextlib import asynccontextmanager



###########################################################################################################################
#
# zde definujte sve GQL modely
# - nove, kde mate zodpovednost
# - rozsirene, ktere existuji nekde jinde a vy jim pridavate dalsi atributy
#
###########################################################################################################################


# from gql_forms.GraphResolvers import resolveRequestsByThreeLetters

from .FormGQLModel import FormGQLModel
from .FormTypeGQLModel import FormTypeGQLModel
from .FormCategoryGQLModel import FormCategoryGQLModel

from .HistoryGQLModel import HistoryGQLModel
from .RequestGQLModel import RequestGQLModel

from .ItemGQLModel import ItemGQLModel
from .ItemTypeGQLModel import ItemTypeGQLModel
from .ItemCategoryGQLModel import ItemCategoryGQLModel

from .SectionGQLModel import SectionGQLModel
from .PartGQLModel import PartGQLModel

from .externals import UserGQLModel, StateGQLModel
from ._GraphPermissions import RoleBasedPermission
# from utils.Dataloaders import getUserFromInfo
from uoishelpers.resolvers import getUserFromInfo

@strawberry.type(description="""Type for query root""")
class Query:
    @strawberry.field(description="""Say hello to the world""")
    async def say_hello_forms(
        self, info: strawberry.types.Info, id: uuid.UUID
    ) -> Union[str, None]:
        user = getUserFromInfo(info)
        result = f"Hello {id} `{user}`"
        return result

    # from .RequestGQLModel import form_test_extension

    from .RequestGQLModel import (
        request_by_id, 
        request_page
    )
    request_by_id = request_by_id
    request_page = request_page

    from .HistoryGQLModel import form_history_by_id
    form_history_by_id = form_history_by_id

    from .FormGQLModel import (
        form_by_id, 
        form_page
    )
    form_by_id = form_by_id
    form_page = form_page
    

    from .FormTypeGQLModel import (
        form_type_by_id,
        form_type_page
    )
    form_type_by_id = form_type_by_id
    form_type_page = form_type_page

    from .FormCategoryGQLModel import (
        form_category_by_id,
        form_category_page
    )
    form_category_by_id = form_category_by_id
    form_category_page = form_category_page

    from .SectionGQLModel import form_section_by_id
    form_section_by_id = form_section_by_id

    from .PartGQLModel import form_part_by_id
    form_part_by_id = form_part_by_id

    from .ItemGQLModel import (
        item_by_id, item_page
    )
    form_item_by_id = item_by_id
    form_item_page = item_page

    from .ItemTypeGQLModel import (
        item_type_by_id, item_type_page
    )
    form_item_type_by_id = item_type_by_id
    form_item_type_page = item_type_page

    from .ItemCategoryGQLModel import (
        item_category_by_id, item_category_page
    )
    item_category_by_id = item_category_by_id
    item_category_page = item_category_page


###########################################################################################################################
#
#
# Mutations
#
#
###########################################################################################################################

   
@strawberry.type(description="""Type for mutation root""")
class Mutation:

    from .FormGQLModel import (
        form_insert,
        form_update
    )
    form_insert = form_insert
    form_update = form_update

    from .ItemGQLModel import (
        item_insert,
        item_update
    )
    form_item_insert = item_insert
    form_item_update = item_update
    #from .HistoryGQLModel import 

    from .ItemTypeGQLModel import (
        form_item_type_insert,
        form_item_type_update
    )
    form_item_type_insert = form_item_type_insert
    form_item_type_update = form_item_type_update

    from .PartGQLModel import (
        part_insert,
        part_update
    )
    form_part_insert = part_insert
    form_part_update = part_update

    from .FormCategoryGQLModel import (
        form_category_insert,
        form_category_update
    )
    form_category_insert = form_category_insert
    form_category_update = form_category_update

    from .SectionGQLModel import (
        section_insert, section_update
    )
    form_section_insert = section_insert
    form_section_update = section_update

    from .RequestGQLModel import (
        form_request_insert, 
        form_request_update,
        form_request_use_transition
    )
    form_request_insert = form_request_insert
    form_request_update = form_request_update
    form_request_use_transition = form_request_use_transition

    from .FormTypeGQLModel import (
        form_type_insert, form_type_update
    )
    form_type_insert = form_type_insert
    form_type_update = form_type_update

    from .HistoryGQLModel import (
        history_insert, history_update
    )
    form_history_insert = history_insert
    form_history_update = history_update

    from .ItemCategoryGQLModel import (
        item_category_update, 
        item_category_insert, 
        item_category_page, 
        item_category_by_id
    )
    form_item_category_update = item_category_update
    form_item_category_insert = item_category_insert
    form_item_category_page = item_category_page
    form_item_category_by_id = item_category_by_id

    

###########################################################################################################################
#
# Schema je pouzito v main.py, vsimnete si parametru types, obsahuje vyjmenovane modely. Bez explicitniho vyjmenovani
# se ve schema objevi jen ty struktury, ktere si strawberry dokaze odvodit z Query. Protoze v teto konkretni implementaci
# nektere modely nejsou s Query propojene je potreba je explicitne vyjmenovat. Jinak ve federativnim schematu nebude
# dostupne rozsireni, ktere tento prvek federace implementuje.
#
###########################################################################################################################

schema = strawberry.federation.Schema(Query, types=(UserGQLModel, StateGQLModel), mutation=Mutation)
