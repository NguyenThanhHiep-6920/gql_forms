import sqlalchemy
from sqlalchemy.schema import Column
from sqlalchemy import Uuid, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .uuid import uuid, UUIDFKey, UUIDColumn, UUID
from .base import BaseModel

class RequestModel(BaseModel):
    __tablename__ = "formrequests"

    id = UUIDColumn()
    name = Column(String, comment="name")
    name_en = Column(String, comment="english name")

    form_id = Column(ForeignKey("forms.id"), comment="Active request form, others are linked by histories")

    created = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="when this entity has been created")
    lastchange = Column(DateTime, server_default=sqlalchemy.sql.func.now(), comment="timestamp / token")
    createdby = UUIDFKey(nullable=True, comment="who's created the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)
    changedby = UUIDFKey(nullable=True, comment="who's changed the entity")#Column(ForeignKey("users.id"), index=True, nullable=True)

    rbacobject = UUIDFKey(nullable=True, comment="user or group id, determines access", default=lambda: UUID("f8089aa6-2c4a-4746-9503-105fcc5d054c"))
    state_id = UUIDFKey(nullable=True, comment="state of the request")

    histories = relationship("HistoryModel", back_populates="request", uselist=True, viewonly=True, lazy="selectin")
    form = relationship("FormModel", uselist=False, viewonly=True, lazy="selectin")