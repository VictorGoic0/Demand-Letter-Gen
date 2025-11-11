"""
LetterTemplate model for firm-specific letter templates.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from shared.base import Base


class LetterTemplate(Base):
    """
    Represents a letter template used for generating demand letters.
    Templates are firm-specific and can be marked as default.
    """
    __tablename__ = "letter_templates"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    letterhead_text = Column(Text, nullable=True)  # Optional letterhead content
    opening_paragraph = Column(Text, nullable=True)  # Opening paragraph text
    closing_paragraph = Column(Text, nullable=True)  # Closing paragraph text
    sections = Column(JSONB, nullable=True)  # Structured sections configuration
    is_default = Column(Boolean, default=False, nullable=False)  # Default template flag
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    firm = relationship("Firm", backref="templates")
    creator = relationship("User", backref="created_templates")

    def __repr__(self):
        return f"<LetterTemplate(id={self.id}, name={self.name}, firm_id={self.firm_id})>"

