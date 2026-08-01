# SmartLearn Agent - Product Design

## User Stories

1. As a **student**, I want to **upload a PDF lecture slide and ask questions about its content**, so that **I can study more efficiently without manually searching through slides**.

2. As a **student**, I want to **get answers with page number citations**, so that **I can quickly find the original content in the PDF to verify the answer**.

3. As a **student**, I want to **ask follow-up questions in a conversation**, so that **I can deepen my understanding of a topic without starting over each time**.

## Feature List

| Priority | Feature | Day |
|----------|---------|-----|
| P0 | PDF text extraction | Day 2 |
| P0 | LLM Q&A with page citation | Day 2 |
| P0 | FastAPI backend | Day 2 |
| P0 | React + Vite frontend | Day 2 |
| P1 | RAG pipeline (chunk + embed + vector search) | Day 3 |
| P1 | Web UI with chat interface | Day 3 |
| P2 | Chat history / multi-turn conversation | Day 3 |
| P2 | Multi-file PDF support | Day 3 |

## What We Will NOT Build

- **User authentication / login** — workshop time is limited, focus on the core AI features
- **OCR for scanned PDFs** — text-based PDFs only; scanned documents are out of scope
- **Mobile app** — web version only
- **Database persistence** — in-memory storage is sufficient for the workshop

## Data Flow

### Day 2: Simple Mode

```
PDF File
  -> [PDF parser (pdfplumber)]    # Extract text from each page
  -> pages[]
  -> [Build prompt]               # Combine pages + question into a prompt
  -> [LLM (DeepSeek)]
  -> Answer with [Page X]
```

### Day 3: RAG Mode

```
PDF -> [Extract text] -> pages
    -> [Split into chunks] -> chunks with source_page
    -> [Embed] -> embeddings (numeric vectors)
    -> [Vector store (FAISS)]   # Store and index embeddings

Question -> [Encode / embed] -> [Similarity search] -> relevant chunks -> [LLM] -> Answer
```
