"""Base model with common attributes"""

from datetime import datetime
from sqlalchemy import Column, DateTime
from app.database.base import Base as DBBase


class Base(DBBase):
    """Base model with common timestamp fields"""

    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
