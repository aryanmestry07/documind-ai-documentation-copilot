from services.document_loader import extract_text_from_pdf
from services.text_chunker import chunk_documents
from services.embedding_service import EmbeddingServices
from services.vector_store import VectorStore


# Step 1: Extract text from PDF
pages = extract_text_from_pdf("data/research-1.pdf")

print("Pages extracted:", len(pages))


# Step 2: Split text into chunks
chunks = chunk_documents(
    pages,
    chunk_size=800,
    overlap=150
)

print("Chunks created:", len(chunks))


# Step 3: Generate embeddings
embedding_service = EmbeddingServices()

texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = embedding_service.generate_embeddings(texts)

print("Embeddings generated:", embeddings.shape)


# Step 4: Store chunks and embeddings in ChromaDB
vector_store = VectorStore()



 
print("Total records in collection:", vector_store.collection.count())


# Step 5: Search for relevant information
question = "How does multi-head attention work?"

print("\nQuestion:", question)

query_embedding = embedding_service.generate_embeddings(
    [question]
)[0]

results = vector_store.search(
    query_embedding,
    n_results=3
)


# Step 6: Display the search results
print("\n--- Search Results ---")

documents = results.get("documents")
metadatas = results.get("metadatas")
distances = results.get("distances")

if not documents or not documents[0]:
    print("No matching chunks found.")

elif metadatas is None or distances is None:
    print("Search results are missing metadata or distances.")

else:
    retrieved_documents = documents[0]
    retrieved_metadatas = metadatas[0]
    retrieved_distances = distances[0]

    for index, text in enumerate(retrieved_documents):
        metadata = retrieved_metadatas[index]
        distance = retrieved_distances[index]

        print(f"\nResult {index + 1}")
        print("Source page:", metadata["page"])
        print("Cosine distance:", round(distance, 4))
        print("Text:", text[:300])