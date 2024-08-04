import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .uuid import UUIDFKey, UUIDColumn
from .base import BaseModel

class FormCategoryModel(BaseModel):
    __tablename__ = "formcategories"

    id = UUIDColumn()
    name = Column(String, comment="name of category")
    name_en = Column(String, comment="english name of category")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="when this entity has been created")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="timestamp / token")
    createdby = UUIDFKey(nullable=True, comment="who's created the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)
    changedby = UUIDFKey(nullable=True, comment="who's changed the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)

    rbacobject = UUIDFKey(nullable=True, comment="user or group id, determines access")

    types = relationship("FormTypeModel", back_populates="category", uselist=True)