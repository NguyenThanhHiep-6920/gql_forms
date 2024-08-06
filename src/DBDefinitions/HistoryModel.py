import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .uuid import uuid, UUIDFKey, UUIDColumn
from .base import BaseModel

class HistoryModel(BaseModel):
    __tablename__ = "formhistories"

    id = UUIDColumn()
    name = Column(String, comment="a notice describing a reason")
    name_en = Column(String, comment="english description")

    request_id = Column(ForeignKey("formrequests.id"), index=True, nullable=True)
    form_id = Column(ForeignKey("forms.id"), index=True, nullable=True)

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="when this entity has been created")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="timestamp / token")
    createdby = UUIDFKey(nullable=True, comment="who's created the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)
    changedby = UUIDFKey(nullable=True, comment="who's changed the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)

    rbacobject = UUIDFKey(nullable=True, comment="user or group id, determines access")
    state_id = UUIDFKey(nullable=True, comment="state of the request")
    
    form = relationship("FormModel", back_populates="history", uselist=False)
    request = relationship("RequestModel", back_populates="histories", uselist=False)