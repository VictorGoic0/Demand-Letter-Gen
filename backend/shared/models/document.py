"""
Document model for uploaded source documents.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from shared.base import Base


class Document(Base):
    """
    Represents an uploaded source document (e.g., medical records, police reports).
    Documents are stored in S3 and referenced by their S3 key.
    """
    __tablename__ = "documents"

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
    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    filename = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    s3_key = Column(String(512), nullable=False, unique=True)  # S3 object key
    mime_type = Column(String(100), nullable=False)  # e.g., 'application/pdf'
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    firm = relationship("Firm", backref="documents")
    uploader = relationship("User", backref="uploaded_documents")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, firm_id={self.firm_id})>"

