import types

import gql_ug

GraphTypeDefinitions: types.ModuleType = src.GraphTypeDefinitions
DBDefinitions: types.ModuleType = src.DBDefinitions
Dataloaders: types.ModuleType = src.utils.Dataloaders
DBFeeder: types.ModuleType = src.DBFeeder

# schema = GraphTypeDefinitions.schema

from src.GraphTypeDefinitions import schema