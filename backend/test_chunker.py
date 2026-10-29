from services.document_loader import extract_text_from_pdf
from services.text_chunker import chunk_documents

file_path = "data/research-1.pdf"

# Step 1: Extract text from the PDF
pages = extract_text_from_pdf(file_path)

# Step 2: Create chunks
chunks = chunk_documents(
    pages,
    chunk_size = 800 ,
    overlap=150
)

# Step 3: Display summary
print(f"Total pages extracted: {len(pages)}")
print(f"Total chunks created: {len(chunks)}")

