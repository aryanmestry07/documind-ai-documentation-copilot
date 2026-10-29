from services.embedding_service import EmbeddingServices
from services.vector_store import VectorStore
from services.llm_service import LLMService

class RAGService:

    def __init__(self):
        self.embedding_service = EmbeddingServices()
        self.vector_store = VectorStore()
        self.llm_service = LLMService()

    def ask(self , question: str) -> dict:

        # Step 1: Convert the questin into an embedding
        query_embedding = self.embedding_service.generate_embeddings(
            [question]
        )[0]

        # Step 2: Retrive relevant chunks from ChromaDB
        results = self.vector_store.search(
            query_embedding,
            n_results= 5
        )

        # Step 3: Extract the retrived text chunks

        documents = results.get("documents")
        metadatas = results.get("metadatas")


        # Step 4: Check whether source documents is available
        if not documents:
            return{
                "answer" : "No relevant documnet information was found.",
                "sources" : []
            }

        # Step 5: Check whether source metadata is available
        if not metadatas or not metadatas[0]:
            return {
                "answer" : "Relevant text was found, but source information is unavailable.",
                "sources" : []
            }

        retrieved_documents = documents[0]
        retrieved_metadatas = metadatas[0]

        print("\n========== RETRIEVED CONTEXT ==========")

        for index, (document, metadata) in enumerate(
            zip(retrieved_documents, retrieved_metadatas),
            start=1
        ):
            print(f"\n--- Chunk {index} ---")
            print(f"Filename: {metadata.get('filename', 'Unknown')}")
            print(f"Page: {metadata.get('page', 'Unknown')}")
            print(document[:500])

        print("\n=======================================\n")


        # Step 6: Combine retrieved chunks into a context string
        context = "\n\n".join(retrieved_documents)

        # Step 7: Generate an answer using Qwen 2.5
        answer = self.llm_service.generate_answer(
            question = question,
            context = context
        )

        # Step 8: Collect source page numbers
        sources = [
            {
                "filename":metadata.get("filename" , "Unknown"),
                "page" : metadata.get("page" , "Unknown")
            }
            for metadata in retrieved_metadatas
            if metadata
        ]

        return {
            "answer" : answer,
            "sources" : sources
        }

