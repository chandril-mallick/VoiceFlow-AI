"""
VoiceFlow AI — Knowledge Document Model
Tracks uploaded documents for RAG with processing status.
"""

import enum
import uuid
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class KnowledgeDocument(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "knowledge_documents"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="pdf/docx/csv/txt/md/url")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, comment="Size in bytes")
    upload_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Processing
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False, index=True
    )
    processing_error: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Qdrant
    qdrant_collection: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Metadata
    metadata_info: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, default=dict,
        comment="Document metadata: title, author, page count, etc."
    )

    # Uploaded by
    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="knowledge_documents")

    def __repr__(self) -> str:
        return f"<KnowledgeDocument {self.filename} ({self.processing_status.value})>"
