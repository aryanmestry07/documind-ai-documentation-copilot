from services.rag_service import RAGService

# Step 1: Initialize the RAG pipeline
rag_service = RAGService()

# Step 2: Get a question from the user
question = input("\nsk DocuMind a question:")

result = rag_service.ask(question)

print("\n====== DOCUMIND ANSWER =========")
print(result["answer"])

print("\n======== SOURCE =======")

for source in result["sources"]:
    print(f"Page: {source['page']}")

