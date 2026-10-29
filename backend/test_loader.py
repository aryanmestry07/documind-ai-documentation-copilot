from services.document_loader import extract_text_from_pdf

file_path = "data/research-1.pdf"

pages = extract_text_from_pdf(file_path)

print(f"Total pages with extracted text: {len(pages)}")


for page in pages:
    print(f"\n--- Pages {['page']} ---")
    print(page["text"][:500])