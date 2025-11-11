"""
GeneratedLetter model for AI-generated demand letters.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from shared.base import Base


class GeneratedLetter(Base):
    """
    Represents a generated demand letter.
    Letters can be in 'draft' or 'created' status.
    When finalized, a .docx file is generated and stored in S3.
    """
    __tablename__ = "generated_letters"

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
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # HTML content of the letter
    status = Column(
        String(50),
        nullable=False,
        default="draft",
        index=True,
    )  # 'draft' or 'created'
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("letter_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    docx_s3_key = Column(String(512), nullable=True)  # S3 key for exported .docx file
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    firm = relationship("Firm", backref="letters")
    creator = relationship("User", backref="created_letters")
    template = relationship("LetterTemplate", backref="letters")
    source_documents = relationship(
        "Document",
        secondary="letter_source_documents",
        backref="letters",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<GeneratedLetter(id={self.id}, title={self.title}, status={self.status})>"

