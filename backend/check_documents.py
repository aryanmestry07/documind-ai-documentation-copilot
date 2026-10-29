from services.vector_store import VectorStore

vector_store = VectorStore()

results = vector_store.collection.get(
    include=["metadatas"]
)

ids = results.get("ids") or []
metadatas = results.get("metadatas") or []

print(f"\nTotal chunks stored: {len(ids)}")

filenames = {}
unknown_examples = []

for chunk_id, metadata in zip(ids, metadatas):
    metadata = metadata or {}

    filename = metadata.get("filename", "Unknown")
    document_id = metadata.get("document_id", "Unknown")

    filenames[filename] = filenames.get(filename, 0) + 1

    if filename == "Unknown" and len(unknown_examples) < 5:
        unknown_examples.append({
            "chunk_id": chunk_id,
            "document_id": document_id,
            "metadata": metadata
        })

print("\nChunks by filename:")

for filename, count in filenames.items():
    print(f"{filename}: {count}")

print("\nExamples of chunks with unknown filenames:")

for example in unknown_examples:
    print(example)

print("\nDatabase inspection complete.")