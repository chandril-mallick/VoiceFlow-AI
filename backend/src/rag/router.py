"""
VoiceFlow AI — Knowledge Base API Router
Upload, manage, and query documents in the RAG knowledge base.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from uuid import UUID

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.auth.dependencies import get_current_user, get_current_tenant_id
from src.models.knowledge import KnowledgeDocument, ProcessingStatus
from src.models.user import User
from src.rag.ingestion import SUPPORTED_TYPES, process_document
from src.rag.retriever import search_knowledge

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResult(BaseModel):
    content: str
    source: str
    score: float


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    processing_status: str
    processing_error: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Upload a document to the knowledge base for RAG processing."""
    # Validate file type
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
    if ext not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {ext}. Supported: {SUPPORTED_TYPES}",
        )

    # Validate file size
    max_size = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {settings.max_upload_size_mb}MB",
        )

    # Save file
    upload_dir = Path(settings.upload_dir) / str(tenant_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Create database record
    doc = KnowledgeDocument(
        tenant_id=tenant_id,
        filename=file.filename,
        file_type=ext,
        file_size=len(content),
        upload_url=str(file_path),
        processing_status=ProcessingStatus.PROCESSING,
        uploaded_by=user.id,
    )
    db.add(doc)
    await db.flush()

    # Process document (in production, this would be a Celery task)
    try:
        result = await process_document(
            file_path=str(file_path),
            file_type=ext,
            tenant_id=str(tenant_id),
        )
        doc.chunk_count = result["chunk_count"]
        doc.qdrant_collection = result["collection_name"]
        doc.processing_status = ProcessingStatus.COMPLETED
    except Exception as e:
        doc.processing_status = ProcessingStatus.FAILED
        doc.processing_error = str(e)[:1000]
        logger.error("Document processing failed: %s", e)

    await db.flush()

    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "status": doc.processing_status.value,
        "chunk_count": doc.chunk_count,
    }


@router.get("/documents")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """List all documents in the knowledge base."""
    result = await db.execute(
        select(KnowledgeDocument)
        .where(KnowledgeDocument.tenant_id == tenant_id)
        .order_by(KnowledgeDocument.created_at.desc())
    )
    docs = result.scalars().all()
    return [
        {
            "id": str(d.id),
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "chunk_count": d.chunk_count,
            "processing_status": d.processing_status.value,
            "processing_error": d.processing_error,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """Delete a document and its vectors from the knowledge base."""
    result = await db.execute(
        select(KnowledgeDocument).where(
            KnowledgeDocument.id == document_id,
            KnowledgeDocument.tenant_id == tenant_id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file from disk
    try:
        if os.path.exists(doc.upload_url):
            os.remove(doc.upload_url)
    except Exception:
        pass

    # TODO: Delete vectors from Qdrant for this specific document

    await db.delete(doc)


@router.post("/query")
async def query_knowledge(
    request: QueryRequest,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """Query the knowledge base with a text search."""
    results = await search_knowledge(
        query=request.query,
        tenant_id=str(tenant_id),
        top_k=request.top_k,
    )
    return {"query": request.query, "results": results, "count": len(results)}
