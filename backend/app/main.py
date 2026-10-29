from fastapi import FastAPI , UploadFile, File, HTTPException
from pydantic import BaseModel
import os
from app.routes.upload import router as upload_router
from services.rag_service import RAGService
from services.vector_store import VectorStore
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware





# Creating FastAPI application
app = FastAPI(
    title = "DocuMind",
    description = "AI-Powered Developer Documentation Copilot",
    version = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(upload_router)
from fastapi.openapi.utils import get_openapi


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    upload_schema = (
        openapi_schema["paths"]["/documents/upload"]["post"]
        ["requestBody"]["content"]["multipart/form-data"]["schema"]
    )

    # Resolve the request-body schema reference
    if "$ref" in upload_schema:
        schema_name = upload_schema["$ref"].split("/")[-1]
        upload_schema = openapi_schema["components"]["schemas"][schema_name]

    upload_schema["properties"]["files"] = {
        "type": "array",
        "items": {
            "type": "string",
            "format": "binary"
        },
        "title": "Files",
        "description": "Upload one or more PDF files"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
# Initializing the RAG Service
rag_service = RAGService()


# Defining the request structure
class QuestionRequest(BaseModel):
    question : str

# Creating a health-check endpoint
@app.get("/heath")
def health_check():
    return{
        "status" : "healthy",
        "application" : "DocuMind"
    }

# question-answering endpoint
@app.post("/ask")
def ask_question(request : QuestionRequest):
    result = rag_service.ask(request.question)

    return result

@app.get("/documents")
def list_documents():
    """List all uploaded documents."""

    try:
        vector_store = VectorStore()
        documents = vector_store.list_documents()

        return{
            "total_documents" : len(documents),
            "documents" : documents
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= f"Failed to retrive documents: {str(e)}"
        ) from e


@app.delete("/documents")
def delete_all_documents():
    """Delete all documents stored in ChromaDB."""

    try:
        vector_store = VectorStore()
        deleted_count = vector_store.delete_all_documents()

        return{
            "message" : "All documents deleted successfully.",
            "deleted_chunks" : deleted_count
        }

    except Exception as e:
        raise HTTPException(
            status_code= 500,
            detail=f"Failed to delete documents: {str(e)}"
        ) from e


@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    """Delete a specific document and its stored chunks."""

    try:
        vector_store = VectorStore()

        # Check whether the document exists.
        documents = vector_store.list_documents()

        document = next(
            (
                item for item in documents
                if item["document_id"] == document_id
            ),
            None
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found."
            )

        # Delete the document's chunks from ChromaDB.
        deleted_chunks = vector_store.delete_document(document_id)

        # Delete the temporary PDF, if it still exists.
        upload_dir = Path("temp_uploads")
        pdf_path = upload_dir / f"{document_id}.pdf"

        if pdf_path.exists():
            pdf_path.unlink()

        return {
            "message": "Document deleted successfully.",
            "document_id": document_id,
            "filename": document["filename"],
            "deleted_chunks": deleted_chunks
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        ) from e