import { useEffect, useRef, useState } from "react";
import "./App.css";
import {
  getDocuments,
  uploadDocuments,
  askQuestion,
  deleteDocument,
} from "./services/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function App() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  // Chat state
  const [chatOpen, setChatOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);
  const [chatError, setChatError] = useState("");

  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);
  const questionInputRef = useRef(null);

  // Fetch documents from FastAPI
  async function loadDocuments() {
    try {
      const data = await getDocuments();
      setDocuments(data.documents || []);
      setError("");
    } catch (err) {
      setError(err.message || "Failed to load documents.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  // Scroll to the latest chat message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, asking]);

  // Focus the question input when chat opens
  useEffect(() => {
    if (chatOpen) {
      setTimeout(() => questionInputRef.current?.focus(), 100);
    }
  }, [chatOpen]);

  // Dashboard statistics
  const totalDocuments = documents.length;

  const totalChunks = documents.reduce(
    (total, document) => total + (document.chunks_count || 0),
    0,
  );

  // Open file selector
  function handleUploadClick() {
    setError("");
    setSuccess("");
    fileInputRef.current?.click();
  }

  // Upload selected PDFs
  async function handleFileChange(event) {
    const selectedFiles = Array.from(event.target.files || []);
    event.target.value = "";

    if (selectedFiles.length === 0) return;

    const invalidFile = selectedFiles.find(
      (file) => !file.name.toLowerCase().endsWith(".pdf"),
    );

    if (invalidFile) {
      setError("Only PDF files are allowed.");
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      const result = await uploadDocuments(selectedFiles);
      const uploadedCount = result.documents?.length || 0;

      setSuccess(
        result.message || `${uploadedCount} document(s) uploaded successfully.`,
      );

      await loadDocuments();
    } catch (err) {
      setError(err.message || "An error occurred while uploading.");
    } finally {
      setUploading(false);
    }
  }

  // Open a fresh chat
  function startNewChat() {
    setMessages([]);
    setQuestion("");
    setChatError("");
    setChatOpen(true);
  }

  // Send a question to the RAG backend
  async function handleAskQuestion(event) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || asking) return;

    if (totalDocuments === 0) {
      setChatError("Upload a PDF before asking questions.");
      return;
    }

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((previous) => [...previous, userMessage]);
    setQuestion("");
    setAsking(true);
    setChatError("");

    try {
      const result = await askQuestion(trimmedQuestion);

      const answerMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: result.answer || "No answer was returned by the AI.",
        sources: Array.isArray(result.sources) ? result.sources : [],
      };

      setMessages((previous) => [...previous, answerMessage]);
    } catch (err) {
      setChatError(
        err.message || "Something went wrong while generating the answer.",
      );
    } finally {
      setAsking(false);
    }
  }

  async function handleDeleteDocument(document) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${document.filename}"?\n\nThis will remove the document and its indexed chunks from DocuMind.`,
    );

    if (!confirmed) return;

    setDeletingId(document.document_id);
    setError("");
    setSuccess("");

    try {
      const result = await deleteDocument(document.document_id);

      // Remove the deleted document from the dashboard immediately.
      setDocuments((previous) =>
        previous.filter((item) => item.document_id !== document.document_id),
      );

      setSuccess(
        result.message || `"${document.filename}" was deleted successfully.`,
      );
    } catch (err) {
      setError(err.message || "Failed to delete document.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="app">
      {/* Hidden PDF input */}{" "}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,application/pdf"
        multiple
        hidden
        onChange={handleFileChange}
      />
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">D</div>
          <h2>DocuMind</h2>
        </div>

        <button className="new-chat-button" onClick={startNewChat}>
          <span>+</span> New conversation
        </button>

        <div className="sidebar-section">
          <p className="sidebar-heading">WORKSPACE</p>

          <button
            className={`sidebar-link ${!chatOpen ? "active" : ""}`}
            onClick={() => setChatOpen(false)}
          >
            <span>▦</span> Overview
          </button>

          <button
            className="sidebar-link"
            onClick={() => {
              setChatOpen(false);
              document
                .getElementById("recent-documents")
                ?.scrollIntoView({ behavior: "smooth" });
            }}
          >
            <span>▤</span> My documents
          </button>

          <button
            className="sidebar-link"
            onClick={() => {
              setChatOpen(false);
              document
                .getElementById("recent-documents")
                ?.scrollIntoView({ behavior: "smooth" });
            }}
          >
            <span>◷</span> Recent activity
          </button>
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot"></div>

          <div>
            <p className="status-title">Local AI engine</p>
            <p className="status-subtitle">Ollama powered</p>
          </div>

          <span className="online-indicator"></span>
        </div>
      </aside>
      {/* Main content */}
      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="breadcrumb">
              Workspace / {chatOpen ? "AI Chat" : "Overview"}
            </p>
          </div>

          <div className="profile">
            <div className="avatar">A</div>
            <span>Personal workspace</span>
          </div>
        </header>

        {chatOpen ? (
          /* AI Chat */
          <section className="chat-page">
            <div className="chat-page-heading">
              <div>
                <p className="eyebrow">YOUR DOCUMENT ASSISTANT</p>
                <h1>
                  Chat with <span>your documents.</span>
                </h1>
                <p>
                  Ask questions and get answers based on your uploaded PDFs.
                </p>
              </div>

              <button
                className="view-all-button"
                onClick={startNewChat}
                disabled={asking}
              >
                + New chat
              </button>
            </div>

            <div className="chat-workspace">
              <div className="chat-messages">
                {messages.length === 0 && (
                  <div className="chat-welcome">
                    <div className="chat-welcome-icon">✳</div>
                    <h2>What would you like to know?</h2>
                    <p>
                      Ask a question about your uploaded documents. DocuMind
                      will retrieve relevant passages and generate an answer.
                    </p>

                    <div className="suggested-questions">
                      <button
                        onClick={() =>
                          setQuestion(
                            "What is the main topic of this document?",
                          )
                        }
                      >
                        What is the main topic of this document?
                      </button>

                      <button
                        onClick={() =>
                          setQuestion("Summarize the key findings.")
                        }
                      >
                        Summarize the key findings
                      </button>

                      <button
                        onClick={() =>
                          setQuestion(
                            "Explain the important concepts in simple words.",
                          )
                        }
                      >
                        Explain the important concepts
                      </button>
                    </div>
                  </div>
                )}

                {messages.map((message) => (
                  <div
                    className={`chat-message ${message.role}`}
                    key={message.id}
                  >
                    <div className="message-avatar">
                      {message.role === "user" ? "A" : "D"}
                    </div>

                    <div className="message-body">
                      <p className="message-author">
                        {message.role === "user" ? "You" : "DocuMind AI"}
                      </p>

                      <div className="message-content">
                        {message.role === "assistant" ? (
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              p: ({ children }) => (
                                <p className="ai-paragraph">{children}</p>
                              ),
                              ol: ({ children }) => (
                                <ol className="ai-list">{children}</ol>
                              ),
                              ul: ({ children }) => (
                                <ul className="ai-list">{children}</ul>
                              ),
                              li: ({ children }) => (
                                <li className="ai-list-item">{children}</li>
                              ),
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        ) : (
                          message.content
                        )}
                      </div>
                      {message.role === "assistant" &&
                        message.sources?.length > 0 && (
                          <div className="source-section">
                            <p className="source-heading">
                              Sources · {message.sources.length}
                            </p>

                            <div className="source-list">
                              {message.sources.map((source, index) => (
                                <div
                                  className="source-item"
                                  key={`${source.filename}-${source.page}-${index}`}
                                >
                                  <span className="source-file-icon">PDF</span>

                                  <div>
                                    <p className="source-filename">
                                      {source.filename}
                                    </p>
                                    <p className="source-page">
                                      Page {source.page}
                                    </p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                    </div>
                  </div>
                ))}

                {asking && (
                  <div className="chat-message assistant">
                    <div className="message-avatar">D</div>
                    <div className="message-body">
                      <p className="message-author">DocuMind AI</p>
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                        <p>Searching documents and generating an answer...</p>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={chatEndRef} />
              </div>

              {chatError && (
                <div className="chat-error" role="alert">
                  {chatError}
                </div>
              )}

              <form className="chat-input-form" onSubmit={handleAskQuestion}>
                <textarea
                  ref={questionInputRef}
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      !event.shiftKey &&
                      !event.nativeEvent.isComposing
                    ) {
                      event.preventDefault();
                      event.currentTarget.form?.requestSubmit();
                    }
                  }}
                  placeholder="Ask anything about your documents..."
                  rows={2}
                  disabled={asking}
                  aria-label="Ask a question about your documents"
                />

                <button
                  type="submit"
                  className="send-message-button"
                  disabled={asking || !question.trim()}
                >
                  {asking ? "Thinking..." : "Send ↑"}
                </button>

                <p className="chat-input-hint">
                  Enter to send · Shift + Enter for a new line
                </p>
              </form>
            </div>
          </section>
        ) : (
          /* Dashboard */
          <section className="dashboard">
            <div className="welcome-section">
              <div>
                <p className="eyebrow">YOUR KNOWLEDGE SPACE</p>

                <h1>
                  Think deeper. <span>Find answers.</span>
                </h1>

                <p className="welcome-description">
                  Upload your documents, ask questions, and let AI help you
                  discover the information that matters.
                </p>
              </div>

              <div className="welcome-decoration">D</div>
            </div>

            {error && (
              <div className="error-message" role="alert">
                {error}
              </div>
            )}

            {success && (
              <div className="success-message" role="status">
                {success}
              </div>
            )}

            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-top">
                  <span>Documents</span>
                  <span className="stat-icon purple">▤</span>
                </div>

                <h2>{loading ? "..." : totalDocuments}</h2>
                <p>Uploaded to your workspace</p>
              </div>

              <div className="stat-card">
                <div className="stat-top">
                  <span>Knowledge chunks</span>
                  <span className="stat-icon blue">◈</span>
                </div>

                <h2>{loading ? "..." : totalChunks}</h2>
                <p>Pieces of information indexed</p>
              </div>

              <div className="stat-card">
                <div className="stat-top">
                  <span>AI engine</span>
                  <span className="stat-icon green">✳</span>
                </div>

                <h2 className="engine-name">Qwen 2.5</h2>
                <p>Running locally with Ollama</p>
              </div>
            </div>

            <div className="section-heading">
              <div>
                <h2>Get started</h2>
                <p>Everything you need to explore your documents.</p>
              </div>
            </div>

            <div className="feature-grid">
              <div className="feature-card upload-card">
                <div className="feature-icon purple">↑</div>
                <h3>Upload documents</h3>

                <p>
                  Add PDF files to your knowledge base and make their content
                  searchable with AI.
                </p>

                <button
                  className="feature-button primary-button"
                  onClick={handleUploadClick}
                  disabled={uploading}
                >
                  {uploading ? "Uploading..." : "Upload a PDF"}
                  <span>{uploading ? "..." : "→"}</span>
                </button>

                {uploading && (
                  <p className="upload-status">
                    Processing your PDFs and generating embeddings. This may
                    take a little while.
                  </p>
                )}
              </div>

              <div className="feature-card chat-card">
                <div className="feature-icon blue">✳</div>
                <h3>Chat with your documents</h3>

                <p>
                  Ask questions about your files and get answers grounded in
                  their content.
                </p>

                <button
                  className="feature-button secondary-button"
                  onClick={startNewChat}
                >
                  Start asking <span>→</span>
                </button>
              </div>
            </div>

            <div
              className="section-heading recent-heading"
              id="recent-documents"
            >
              <div>
                <h2>Recent documents</h2>

                <p>
                  {loading
                    ? "Loading your documents..."
                    : `${totalDocuments} document${
                        totalDocuments === 1 ? "" : "s"
                      } in your knowledge base`}
                </p>
              </div>

              <button
                className="view-all-button"
                onClick={loadDocuments}
                disabled={loading}
              >
                Refresh ↻
              </button>
            </div>

            {loading && (
              <div className="empty-state">
                <p>Loading documents...</p>
              </div>
            )}

            {!loading && !error && documents.length > 0 && (
              <div className="document-list">
                {documents.map((document) => (
                  <div className="document-row" key={document.document_id}>
                    <div className="document-file-icon">PDF</div>

                    <div className="document-info">
                      <h3>{document.filename}</h3>
                      <p>{document.chunks_count} knowledge chunks</p>
                    </div>

                    <div className="document-actions">
                      <span className="document-status">Indexed</span>

                      <button
                        className="delete-document-button"
                        onClick={() => handleDeleteDocument(document)}
                        disabled={deletingId === document.document_id}
                        aria-label={`Delete ${document.filename}`}
                      >
                        {deletingId === document.document_id
                          ? "Deleting..."
                          : "Delete"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!loading && !error && documents.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">▤</div>
                <h3>Your knowledge base starts here</h3>

                <p>Upload your first PDF to begin exploring your documents.</p>

                <button
                  className="feature-button primary-button empty-upload-button"
                  onClick={handleUploadClick}
                  disabled={uploading}
                >
                  Upload a PDF <span>→</span>
                </button>
              </div>
            )}

            <footer className="dashboard-footer">
              <span>DocuMind</span>
              <span>Your documents. Your AI. Your knowledge.</span>
            </footer>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
