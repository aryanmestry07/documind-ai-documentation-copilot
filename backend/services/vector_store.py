import chromadb
import uuid


class VectorStore:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.client = chromadb.PersistentClient(
            path = persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name = "documind_documents",
            metadata = {"hnsw:space" : "cosine"}
        )

    def add_chunks(self,chunks : list[dict],embeddings , document_id : str , filename : str) -> list[str]:
        if not chunks:
            return []

        ids = [str(uuid.uuid4()) for _ in chunks]

        metadatas = []

        for chunk in chunks:
             metadata = chunk["metadata"].copy()
             metadata["document_id"] = document_id
             metadata["filename"] = filename

             metadatas.append(metadata)

        self.collection.add(
            ids = ids,
            documents=[chunk["text"] for chunk in chunks],
            embeddings= embeddings.tolist(),
            metadatas= metadatas
        )

        return ids

    def search(self, query_embedding, n_results: int = 5):
        """Retrieve relevant, non-duplicate chunks from ChromaDB."""

        total_chunks = self.collection.count()

        if total_chunks == 0:
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

        # Retrieve extra candidates so duplicates can be skipped.
        candidate_count = min(n_results * 4, total_chunks)

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=candidate_count,
            include=["documents", "metadatas", "distances"]
        )

        # Extract the results safely.
        ids_by_query = results.get("ids")
        documents_by_query = results.get("documents")
        metadatas_by_query = results.get("metadatas")
        distances_by_query = results.get("distances")

        retrieved_ids = ids_by_query[0] if ids_by_query else []
        retrieved_documents = (
            documents_by_query[0] if documents_by_query else []
        )
        retrieved_metadatas = (
            metadatas_by_query[0] if metadatas_by_query else []
        )
        retrieved_distances = (
            distances_by_query[0] if distances_by_query else []
        )

        # Remove duplicate text chunks.
        unique_results = []
        seen_texts = set()

        for chunk_id, document, metadata, distance in zip(
            retrieved_ids,
            retrieved_documents,
            retrieved_metadatas,
            retrieved_distances
        ):
            if not document or not document.strip():
                continue

            # Normalize whitespace and case to detect identical text.
            normalized_text = " ".join(document.split()).casefold()

            if normalized_text in seen_texts:
                continue

            seen_texts.add(normalized_text)

            unique_results.append({
                "id": chunk_id,
                "document": document,
                "metadata": metadata or {},
                "distance": distance
            })

            if len(unique_results) >= n_results:
                break

        # Return results in ChromaDB's expected structure.
        return {
            "ids": [[item["id"] for item in unique_results]],
            "documents": [[item["document"] for item in unique_results]],
            "metadatas": [[item["metadata"] for item in unique_results]],
            "distances": [[item["distance"] for item in unique_results]]
        }

    def delete_all_documents(self):
         """Delete all stored chunks from the DocuMind collection."""
         total_chunks = self.collection.count()

         if total_chunks > 0:
            self.collection.delete(
            ids=self.collection.get()["ids"]
            )


         return total_chunks

    def delete_document(self,document_id: str):
        """Delete all chunks belonging to a specific document."""

        results = self.collection.get(
            where = {"document_id" : document_id},
            include = ["metadatas"]
        )

        chunk_ids = results.get("ids", [])

        if not chunk_ids:
            return 0

        self.collection.delete(ids=chunk_ids)

        return len(chunk_ids)


    def list_documents(self):
        """Return uploaded documents and their chunk counts."""

        results = self.collection.get(
            include = ["metadatas"]
        )
        metadatas = results.get("metadatas") or []

        documents  = {}

        for metadata in metadatas:
            if not metadata:
                continue

            document_id = metadata.get("document_id")
            filename = metadata.get("filename")

            if not document_id or not filename:
                continue

            if document_id not in documents:
                documents[document_id] = {
                    "document_id" : document_id,
                    "filename" : filename,
                    "chunks_count" : 0
                }

            documents[document_id]["chunks_count"] += 1

        return list(documents.values())
