from uoishelpers.resolvers import createDBResolvers, DBResolver

from src.DBDefinitions import (
    BaseModel,
    FormCategoryModel,
    FormTypeModel,
    FormModel,
    ItemCategoryModel,
    ItemTypeModel,
    ItemModel,
    PartModel,
    SectionModel,

    HistoryModel,
    RequestModel,
)

DBResolvers = createDBResolvers(BaseModel)

FormCategoryResolvers = DBResolver(FormCategoryModel)
FormTypeResolvers = DBResolver(FormTypeModel)
FormResolvers = DBResolver(FormModel)
ItemCategoryResolvers = DBResolver(ItemCategoryModel)
ItemTypeResolvers = DBResolver(ItemTypeModel)
ItemResolvers = DBResolver(ItemModel)
PartResolvers = DBResolver(PartModel)
SectionResolvers = DBResolver(SectionModel)

HistoryResolvers = DBResolver(HistoryModel)
RequestResolvers = DBResolver(RequestModel)
