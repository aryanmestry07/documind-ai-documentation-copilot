import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException

from services.document_loader import extract_text_from_pdf
from services.text_chunker import chunk_documents
from services.embedding_service import EmbeddingServices
from services.vector_store import VectorStore


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

# Temporary upload directory
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize services
embedding_service = EmbeddingServices()
vector_store = VectorStore()

# Intended document retention period
DOCUMENT_RETENTION_HOURS = 24


@router.post("/upload")
async def upload_documents(
    files: Annotated[
        list[UploadFile],
        File(description="Select one or more PDF files")
    ]
):
    uploaded_documents = []

    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one PDF."
        )

    for file in files:
        try:
            # Validate filename and extension
            if (
                not file.filename
                or Path(file.filename).suffix.lower() != ".pdf"
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Only PDF files are allowed."
                )

            # Generate a unique document ID
            document_id = str(uuid.uuid4())
            temporary_path = UPLOAD_DIR / f"{document_id}.pdf"

            # Read uploaded file
            contents = await file.read()

            if not contents:
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} is empty."
                )

            # Save PDF temporarily
            with temporary_path.open("wb") as pdf_file:
                pdf_file.write(contents)

            # Extract text from PDF
            pages = extract_text_from_pdf(str(temporary_path))

            if not pages:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"No extractable text found in "
                        f"{file.filename}."
                    )
                )

            # Split extracted text into chunks
            chunks = chunk_documents(
                pages=pages,
                chunk_size=800,
                overlap=150
            )

            if not chunks:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"No text chunks could be created for "
                        f"{file.filename}."
                    )
                )

            # Generate embeddings
            texts = [chunk["text"] for chunk in chunks]
            embeddings = embedding_service.generate_embeddings(texts)

            # Store chunks and metadata in ChromaDB
            stored_ids = vector_store.add_chunks(
                chunks=chunks,
                embeddings=embeddings,
                document_id=document_id,
                filename=file.filename
            )

            # Calculate intended expiration time
            uploaded_at = datetime.now(timezone.utc)
            expires_at = uploaded_at + timedelta(
                hours=DOCUMENT_RETENTION_HOURS
            )

            uploaded_documents.append({
                "document_id": document_id,
                "filename": file.filename,
                "pages_processed": len(pages),
                "chunks_stored": len(stored_ids),
                "uploaded_at": uploaded_at.isoformat(),
                "expires_at": expires_at.isoformat()
            })

        finally:
            await file.close()

    return {
        "message": "Documents uploaded and indexed successfully.",
        "documents": uploaded_documents
    }