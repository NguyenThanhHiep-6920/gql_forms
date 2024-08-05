import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .uuid import UUIDFKey, UUIDColumn
from .base import BaseModel

class PartModel(BaseModel):
    __tablename__ = "formparts"

    id = UUIDColumn()
    name = Column(String, comment="name of part")
    name_en = Column(String, comment="english name of part")
    order = Column(Integer, comment="order in parent entity")

    section_id = Column(ForeignKey("formsections.id"), index=True)

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="when this entity has been created")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="timestamp / token")
    createdby = UUIDFKey(nullable=True, comment="who's created the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)
    changedby = UUIDFKey(nullable=True, comment="who's changed the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)

    rbacobject = UUIDFKey(nullable=True, comment="user or group id, determines access")
    state_id = UUIDFKey(nullable=True, comment="state of the request")
    
    section = relationship("SectionModel", back_populates="parts", uselist=False)
    items = relationship("ItemModel", back_populates="part", uselist=True)