const API_BASE_URL = "http://127.0.0.1:8000";

// Fetch all uploaded documents
export async function getDocuments() {
  const response = await fetch(`${API_BASE_URL}/documents`);

  if (!response.ok) {
    throw new Error("Failed to fetch documents.");
  }

  return response.json();
}

// Upload one or more PDF files
export async function uploadDocuments(files) {
  const formData = new FormData();

  // The field name must match the FastAPI parameter: files
  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail || data.message || "Failed to upload documents."
    );
  }

  return data;
}

// Ask a question about uploaded documents
export async function askQuestion(question) {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: question,
    }),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail || data.message || "Failed to get an answer."
    );
  }

  return data;
}


// Delete a specific document
export async function deleteDocument(documentId) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${encodeURIComponent(documentId)}`,
    {
      method: "DELETE",
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail || data.message || "Failed to delete document."
    );
  }

  return data;
}