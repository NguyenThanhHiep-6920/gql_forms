import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .uuid import UUIDFKey, UUIDColumn
from .base import BaseModel

class ItemTypeModel(BaseModel):
    __tablename__ = "formitemtypes"

    id = UUIDColumn()
    name = Column(String, comment="name of type")
    name_en = Column(String, comment="english name of type")

    query = Column(String, comment="could be API query associated with item type `/students/%`")
    selector = Column(String, comment="could be used for picking up the right value from query `result;item;id` ")

    category_id = Column(ForeignKey("formitemcategories.id"), index=True)

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="when this entity has been created")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="timestamp / token")
    createdby = UUIDFKey(nullable=True, comment="who's created the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)
    changedby = UUIDFKey(nullable=True, comment="who's changed the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)

    rbacobject = UUIDFKey(nullable=True, comment="user or group id, determines access")

    items = relationship("ItemModel", back_populates="type", uselist=True)
    category = relationship("ItemCategoryModel", back_populates="types", uselist=False)