import pymupdf 

def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF , page by page.

    Return a list containing each page's text and metadata.
    """

    extracted_pages = []

    with pymupdf.open(file_path) as document:
        for page_number , page in enumerate(document, start = 1): # type: ignore

            text = page.get_text("text").strip()

            if text:
                extracted_pages.append({
                    "text" : text,
                    "page" : page_number
                })
        return extracted_pages
