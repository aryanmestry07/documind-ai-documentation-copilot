from services.embedding_service import EmbeddingServices

embedding_service = EmbeddingServices()

texts = [
    "Self-attention helps Transformers understand relationships between tokens.",
    "Multi-head attention allows a model to attend to information from different representation subspaces.",
    "I enjoy eating pizza and chocolate cake."
]

embeddings = embedding_service.generate_embeddings(texts)

print("Number of texts: " , len(texts))
print("Embedding shape: " , embeddings.shape)

for index , embedding in enumerate(embeddings , start=1):
    print(f"\nText {index}")
    print("Vector dimensions:" , len(embedding))
    print("First five values:" , embedding[:5])