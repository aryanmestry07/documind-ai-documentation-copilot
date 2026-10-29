# DocuMind – AI-Powered Documentation Assistant

DocuMind is an AI-powered documentation assistant that allows users to upload PDF documents, ask questions about their content, and receive context-aware answers with source citations. It uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from documents and generate answers using a locally running Large Language Model (LLM).

The application combines a React frontend with a FastAPI backend, semantic search, vector storage, and local LLM inference to provide an interactive document question-answering experience.

## Features

* **PDF Upload:** Upload PDF documents to build a searchable knowledge base.
* **Document Processing:** Extract text from PDFs and divide it into smaller chunks for efficient retrieval.
* **Semantic Search:** Generate text embeddings and retrieve relevant document passages based on user questions.
* **Retrieval-Augmented Generation:** Use retrieved document context to generate relevant answers.
* **AI-Powered Question Answering:** Ask natural-language questions about uploaded documents.
* **Source Citations:** Display source filenames and page numbers alongside generated answers.
* **Document Management:** View uploaded documents and their indexed knowledge chunks.
* **Document Deletion:** Remove individual documents and their associated indexed chunks.
* **Interactive Dashboard:** Manage documents and access the AI chat interface through a React-based user interface.
* **Local LLM Inference:** Generate answers using Qwen 2.5 through Ollama.

## Technology Stack

### Frontend

* React.js
* JavaScript
* HTML
* CSS
* React Markdown

### Backend

* Python
* FastAPI
* Uvicorn
* PyMuPDF

### AI and Machine Learning

* Retrieval-Augmented Generation (RAG)
* Sentence Transformers
* `all-MiniLM-L6-v2` for text embeddings
* Qwen 2.5 for answer generation
* Ollama for local LLM inference

### Vector Database

* ChromaDB

### Development Tools

* Visual Studio Code
* Git
* GitHub
* npm

## System Architecture

DocuMind follows a Retrieval-Augmented Generation architecture.

### Document Ingestion

1. The user uploads a PDF through the React frontend.
2. The FastAPI backend extracts text from the PDF using PyMuPDF.
3. The extracted text is divided into smaller chunks.
4. Sentence Transformers converts the chunks into numerical embeddings.
5. ChromaDB stores the embeddings, text chunks, and associated metadata.

### Question Answering

1. The user submits a natural-language question.
2. The question is converted into an embedding using Sentence Transformers.
3. ChromaDB retrieves the most relevant document chunks.
4. The retrieved passages are combined into a context for the language model.
5. Qwen 2.5 generates an answer using the retrieved context.
6. The frontend displays the answer along with available source filenames and page numbers.

## Project Structure

The project is organized into separate frontend and backend applications.

```text
documind-ai-documentation-copilot/
|
|-- backend/
|   |-- app/
|   |-- routes/
|   |-- services/
|   |-- requirements.txt
|   |-- app/main.py
|
|-- frontend/
|   |-- public/
|   |-- src/
|   |-- package.json
|
|-- .gitignore
|-- README.md
```

The exact directory structure may vary depending on the current implementation.

## Prerequisites

Before running DocuMind locally, install the following:

* Python 3.10 or a compatible version supported by the project dependencies
* Node.js and npm
* Git
* Ollama
* The Qwen 2.5 model supported by your local Ollama installation

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/aryanmestry07/documind-ai-documentation-copilot.git
cd documind-ai-documentation-copilot
```

### 2. Set Up the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Set Up Ollama

Install Ollama from the official website:

https://ollama.com/

Download the Qwen 2.5 model:

```bash
ollama pull qwen2.5:7b
```

Ensure Ollama is running and the model is available before using the question-answering functionality.

### 4. Start the Backend

From the backend directory, run:

```bash
uvicorn app.main:app --reload
```

The FastAPI backend should be available at:

`http://127.0.0.1:8000`

Access the interactive API documentation at:

`http://127.0.0.1:8000/docs`

### 5. Set Up the Frontend

Open another terminal and navigate to the frontend directory from the project root:

```bash
cd frontend
```

Install the frontend dependencies:

```bash
npm install
```

Start the React development server:

```bash
npm run dev
```

Open the local URL displayed in the terminal, typically:

`http://localhost:5173`

If that port is already occupied, Vite may select another available port.

## Usage

1. Start the Ollama model and backend server.
2. Start the React frontend.
3. Open DocuMind in your browser.
4. Upload one or more PDF documents.
5. Wait for the documents to be processed and indexed.
6. Open the AI chat interface.
7. Ask questions about the uploaded documents.
8. Review the generated answers and their source citations.
9. Manage your uploaded documents from the dashboard.

## Current Limitations

* Answer quality depends on the relevance and quality of the retrieved document chunks.
* The language model may generate inaccurate information if the retrieved context is insufficient.
* Local LLM inference requires sufficient system memory and computational resources.
* The application currently focuses on PDF document processing.
* Deployment requires an environment capable of supporting the backend, vector storage, and selected LLM inference setup.

## Future Improvements

Potential improvements include:

* Conversation history and persistent chat sessions
* Document summarization
* Improved source passages and citation navigation
* Advanced retrieval techniques, including hybrid search and reranking
* Retrieval evaluation and answer-quality metrics
* Support for additional document formats
* Improved document filtering and search
* Docker-based deployment
* Production-ready authentication and access controls

## Learning Outcomes

This project provides practical experience with:

* Building a RAG pipeline
* Text extraction and chunking
* Generating and storing text embeddings
* Semantic retrieval using a vector database
* Integrating a locally hosted language model
* Developing REST APIs with FastAPI
* Building an interactive frontend with React
* Connecting frontend and backend services
* Managing document metadata and source citations

## Author

**Aryan Mestry**

BCA Graduate | AI/ML Enthusiast | Full-Stack Developer

GitHub: https://github.com/aryanmestry07

## License

A license has not yet been specified. Add a license file if you intend to distribute the project under specific terms.
