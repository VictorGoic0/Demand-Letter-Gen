"""
Firm model for multi-tenancy.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from shared.base import Base


class Firm(Base):
    """
    Represents a law firm (tenant).
    Each firm has its own users, documents, templates, and letters.
    """
    __tablename__ = "firms"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<Firm(id={self.id}, name={self.name})>"

