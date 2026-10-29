from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(
        pages : list[dict],
        chunk_size : int = 800,
        overlap : int = 150
) -> list[dict]: # type: ignore
    """
    Split extracted page text into smaller overlapping chunks.

    preserve the page number for source tracking.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = overlap,
        separators=["\n\n" , "\n" , " ",""]
    )

    chunks = []

    for page in pages:
        page_chunks = splitter.split_text(page["text"])

        for chunk_text in page_chunks:
            chunks.append({
                "text" : chunk_text,
                "metadata" : {
                    "page" : page["page"]
                }
            })
    return chunks
