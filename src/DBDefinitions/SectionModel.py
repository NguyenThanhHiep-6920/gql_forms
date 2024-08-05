import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy.orm import relationship
from sqlalchemy import Uuid, String, DateTime, ForeignKey, Integer

from .uuid import UUIDFKey, UUIDColumn
from .base import BaseModel

class SectionModel(BaseModel):
    __tablename__ = "formsections"

    # requestId = Column(ForeignKey("requests.id"), primary_key=True)
    # key is st sys structure name pr as id, fk follpw by id in lower letter

    id = UUIDColumn()
    name = Column(String, comment="name")
    name_en = Column(String, comment="english name")

    form_id = Column(ForeignKey("forms.id"), index=True)
    order = Column(Integer, comment="order in parent entity")
    status = Column(String)

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="when this entity has been created")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="timestamp / token")
    createdby = UUIDFKey(nullable=True, comment="who's created the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)
    changedby = UUIDFKey(nullable=True, comment="who's changed the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)

    rbacobject = UUIDFKey(nullable=True, comment="user or group id, determines access")
    state_id = UUIDFKey(nullable=True, comment="state of the request")
    
    form = relationship("FormModel", back_populates="sections")
    parts = relationship("PartModel", back_populates="section", uselist=True)
