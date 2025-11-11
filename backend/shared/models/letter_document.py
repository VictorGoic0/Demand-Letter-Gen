"""
LetterSourceDocument junction table for many-to-many relationship
between generated letters and source documents.
"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from shared.base import Base


class LetterSourceDocument(Base):
    """
    Junction table model for the many-to-many relationship
    between GeneratedLetter and Document.
    """
    __tablename__ = "letter_source_documents"

    letter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("generated_letters.id", ondelete="CASCADE"),
        primary_key=True,
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )

    def __repr__(self):
        return f"<LetterSourceDocument(letter_id={self.letter_id}, document_id={self.document_id})>"

