import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .uuid import uuid, UUIDFKey, UUIDColumn
from .base import BaseModel

class FormTypeModel(BaseModel):
    __tablename__ = "formtypes"

    id = UUIDColumn()
    name = Column(String, comment="name of type")
    name_en = Column(String, comment="english name of type")

    category_id = Column(ForeignKey("formcategories.id"), index=True, nullable=True)

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="when this entity has been created")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="timestamp / token")
    createdby = UUIDFKey(nullable=True, comment="who's created the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)
    changedby = UUIDFKey(nullable=True, comment="who's changed the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)

    rbacobject = UUIDFKey(nullable=True, comment="user or group id, determines access")

    forms = relationship("FormModel", back_populates="type", uselist=True)
    category = relationship("FormCategoryModel", back_populates="types")
