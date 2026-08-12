# DocQuery

## AI-Powered Document Question Answering using RAG

DocQuery is an AI-powered document question-answering application designed to help **nonprofit organization staff** quickly find reliable information from documents such as **grant guidelines, donor agreements, and impact reports**.

Instead of manually searching through multiple documents, users can log in, upload documents, and ask questions in natural language. DocQuery uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded documents and uses **Gemini AI** to generate grounded answers with source references.

The system maintains user-specific documents and data so users can return later without uploading their documents again.

---

## Problem Statement

A nonprofit organization may have grant guidelines, donor agreements, impact reports, and other important documents, but staff often cannot quickly answer questions because the required information is scattered across multiple documents.

Manually searching these documents can be time-consuming and may lead to missed or incorrect information.

DocQuery solves this by providing a single interface where users can upload their documents and ask questions about them using natural language.

---

## Solution

DocQuery allows users to:

1. Create an account and log in.
2. Upload organizational PDF documents.
3. Store their documents for future access.
4. Ask questions in natural language.
5. Retrieve relevant information from their uploaded documents.
6. Generate answers using Gemini AI.
7. View the source document and page associated with the answer.
8. Return later and continue using their previously uploaded documents.

The system is designed to answer questions based on uploaded documents rather than relying on unsupported information.

---

## How DocQuery Works

```text
                         User
                           |
                           v
                    Login / Sign Up
                           |
                           v
                     Streamlit UI
                           |
                           v
                   Upload Documents
                           |
                           v
                     FastAPI API
                           |
                           v
                  Extract PDF Text
                           |
                           v
                     Clean Text
                           |
                           v
                      Chunking
                           |
                           v
                      Metadata
                           |
                           v
                 Gemini Embeddings
                           |
                           v
                       ChromaDB
                           |
                           |
                   User asks a question
                           |
                           v
                  Question Embedding
                           |
                           v
               Vector Similarity Search
                           |
                           v
                     Top-K Chunks
                           |
                           v
                   Relevant Context
                           |
                           v
                      Gemini AI
                           |
                           v
                   Answer + Sources
```

---

# RAG Pipeline

## Document Processing

```text
Document
   ↓
PDF Text Extraction
   ↓
Text Cleaning
   ↓
Chunking
   ↓
Metadata
   ↓
Embeddings
   ↓
ChromaDB
```

## Question Answering

```text
User Question
      ↓
Question Embedding
      ↓
ChromaDB Search
      ↓
Top-K Relevant Chunks
      ↓
Relevant Context
      ↓
Gemini AI
      ↓
Grounded Answer
      ↓
Source Citation
```

---

# Authentication and Data Persistence

DocQuery includes authentication so that each user's documents and application data remain associated with their account.

```text
User
 ↓
Login / Sign Up
 ↓
User ID
 ↓
User's Documents
 ↓
Document Metadata
 ↓
ChromaDB Retrieval Data
```

For example:

```text
User A
 ├── Grant_Guidelines.pdf
 ├── Donor_Agreement.pdf
 └── Impact_Report.pdf

User B
 ├── Company_Policy.pdf
 └── Project_Report.pdf
```

When a user returns and logs in again, their previously uploaded documents remain available.

Authentication and persistent storage make DocQuery more practical for repeated organizational use.

---

# Key Features

* User registration and login
* User-specific document storage
* PDF document upload
* PDF text extraction
* Text cleaning and chunking
* Metadata management
* Embedding generation
* ChromaDB vector storage
* Vector similarity search
* Top-K retrieval
* Gemini AI answer generation
* Source and page citations
* Grounded responses
* `"I don't know"` fallback
* Document library
* Basic retrieval and answer evaluation
* Streamlit interface
* FastAPI backend

---

# Example

## User Question

> What are the reporting requirements for the grant?

## DocQuery Response

> The organization must submit an annual impact report covering program outcomes and fund utilization.

**Source:** `Grant_Guidelines.pdf — Page 12`

---

# Grounded Answers

DocQuery is designed to generate answers using information retrieved from uploaded documents.

The system should:

* Use the retrieved document context.
* Avoid unsupported information.
* Avoid relying on outside knowledge for document-specific questions.
* Provide the source of the retrieved information.
* Clearly indicate when sufficient information is not available.

If the answer cannot be found:

> I couldn't find enough information in the provided documents to answer this question.

This helps reduce unsupported or hallucinated responses.

---

# Source Citations

Each document chunk contains metadata such as:

```json
{
  "user_id": "user_001",
  "document_name": "Grant_Guidelines.pdf",
  "document_type": "Grant Guidelines",
  "page": 12,
  "section": "Reporting Requirements",
  "chunk_id": "grant_001_12_03"
}
```

Example:

```text
Answer:
The organization must submit an annual impact report.

Source:
Grant_Guidelines.pdf
Page: 12
Section: Reporting Requirements
```

---

# Technology Stack

| Technology            | Purpose                                       |
| --------------------- | --------------------------------------------- |
| **Python**            | Main programming language                     |
| **Streamlit**         | User interface                                |
| **Figma**             | UI/UX design                                  |
| **FastAPI**           | Backend API                                   |
| **PostgreSQL**        | User accounts and persistent application data |
| **PyPDF**             | PDF text extraction                           |
| **LangChain**         | RAG pipeline orchestration                    |
| **Gemini API**        | AI answer generation                          |
| **Gemini Embeddings** | Convert text into vector representations      |
| **ChromaDB**          | Vector database and similarity search         |
| **python-dotenv**     | Environment variable management               |
| **Git**               | Version control                               |
| **GitHub**            | Team collaboration                            |

> The exact Gemini embedding model will be finalized based on the available Gemini API/model support during implementation.

---

# Data Storage

## User and Application Data

PostgreSQL is used to store structured application data such as:

* Users
* Documents
* Document metadata
* User-document relationships

Example:

```text
User
 ↓
Documents
 ↓
Document Metadata
```

The document metadata stored in PostgreSQL identifies which user owns each document.

## Uploaded Documents

During the MVP, uploaded PDFs can be stored locally:

```text
data/
└── documents/
    ├── grant_guidelines.pdf
    ├── donor_agreement.pdf
    └── impact_report.pdf
```

Cloud object storage can be added later for production deployment.

## Embeddings and Retrieval Data

Document embeddings and retrieval metadata are stored in:

```text
ChromaDB
```

## API Keys

API credentials are stored in:

```text
.env
```

The `.env` file must never be committed to GitHub.

---

# Project Structure

```text
DocQuery/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── upload.py
│   │   └── query.py
│   │
│   ├── ingestion/
│   │   ├── loader.py
│   │   ├── cleaner.py
│   │   ├── chunker.py
│   │   └── metadata.py
│   │
│   ├── embeddings/
│   │   └── embedder.py
│   │
│   ├── retrieval/
│   │   ├── vector_store.py
│   │   └── retriever.py
│   │
│   ├── generation/
│   │   ├── llm.py
│   │   └── prompts.py
│   │
│   └── database/
│       ├── models.py
│       └── database.py
│
├── frontend/
│   └── streamlit_app.py
│
├── data/
│   └── documents/
│
├── chroma_db/
│
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# API Endpoints

## Authentication

### `POST /auth/register`

Creates a new user account.

### `POST /auth/login`

Authenticates an existing user.

---

## Document Upload

### `POST /upload`

Uploads and processes a document.

```text
Document
   ↓
Extract Text
   ↓
Clean
   ↓
Chunk
   ↓
Generate Embeddings
   ↓
Store in ChromaDB
   ↓
Save Document Metadata
```

---

## Question Answering

### `POST /query`

Accepts a natural-language question and returns a grounded answer.

### Request

```json
{
  "question": "What are the reporting requirements?"
}
```

### Response

```json
{
  "answer": "The organization must submit an annual impact report.",
  "sources": [
    {
      "document": "Grant_Guidelines.pdf",
      "page": 12,
      "section": "Reporting Requirements"
    }
  ]
}
```

---

# Setup

## 1. Clone the Repository

```bash
git clone <repository-url>
cd DocQuery
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

## 3. Activate the Virtual Environment

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key
DATABASE_URL=your_postgresql_connection_string
```

Never commit the `.env` file to GitHub.

---

# Running the Application

## Start FastAPI Backend

```bash
uvicorn app.main:app --reload
```

## Start Streamlit Frontend

```bash
streamlit run frontend/streamlit_app.py
```

---

# User Flow

```text
Landing Page
      ↓
Login / Sign Up
      ↓
User Dashboard
      ↓
Upload Document
      ↓
Document Processing
      ↓
Document Library
      ↓
Ask Question
      ↓
RAG Retrieval
      ↓
Gemini Answer
      ↓
Answer + Source
```

When the user returns later:

```text
Login
  ↓
Dashboard
  ↓
Previously Uploaded Documents
  ↓
Continue Asking Questions
```

---

# Team Responsibilities

The project is divided between two team members for documentation and ownership.

## Member 1 — Frontend / UI/UX

* Figma design
* Streamlit interface
* Login and signup interface
* Dashboard
* Document library
* Document upload interface
* Question input
* Chat interface
* Answer display
* Source display
* Frontend integration

## Member 2 — Backend / RAG / AI

* FastAPI setup
* Authentication backend
* PostgreSQL integration
* Document upload API
* PDF processing
* Text extraction
* Text cleaning
* Chunking
* Metadata
* Embeddings
* ChromaDB
* Retrieval
* Gemini integration
* Prompt design
* API integration

> Although ownership is divided for documentation, both team members will understand and contribute to the complete frontend and backend workflow so that either member can explain the project during the final presentation.

---

# Evaluation

DocQuery will be evaluated at both the retrieval and answer levels.

## Retrieval Evaluation

* Recall@K
* Precision@K

## Answer Evaluation

* Correctness
* Groundedness
* Citation accuracy
* Appropriate `"I don't know"` responses

## Example Evaluation Questions

| Question                             | Expected Source  |
| ------------------------------------ | ---------------- |
| What are the reporting requirements? | Grant Guidelines |
| What expenses are eligible?          | Grant Guidelines |
| When is the report due?              | Donor Agreement  |
| What outcomes were achieved?         | Impact Report    |

---

# Scope

## In Scope

* User registration and login
* User-specific data
* Document upload
* PDF processing
* Text extraction
* Text cleaning
* Document chunking
* Metadata management
* Embedding generation
* ChromaDB vector database
* Vector similarity search
* Top-K retrieval
* RAG-based question answering
* Gemini AI integration
* Grounded responses
* Source citations
* `"I don't know"` fallback
* Streamlit interface
* FastAPI backend
* PostgreSQL application data
* Basic evaluation
* Deployment

## Out of Scope

* Mobile application
* Voice assistant
* LLM fine-tuning
* Training a custom embedding model
* Multi-organization SaaS architecture
* Advanced enterprise SSO
* Payment integration
* WhatsApp integration
* Complex autonomous agent workflows
* Custom model training

---

# Improvements from the Initial Approach

The initial RAG architecture is retained while the application is extended to support persistent user data.

## Gemini Instead of OpenAI

Gemini is used for answer generation and the planned embedding layer, allowing the team to work primarily with one AI ecosystem and simplify API management.

## Streamlit for the Frontend

Streamlit provides a fast way to build the document upload, document library, and question-answer interface while allowing the team to focus more effort on the RAG pipeline.

## Authentication Added

Authentication is included because users need to return to the application and access their previously uploaded documents.

## PostgreSQL Added

PostgreSQL is used to store user accounts, document metadata, and relationships between users and their documents.

## Local Document Storage for MVP

Uploaded PDFs can remain in local storage during the MVP. Cloud object storage can be added later if the project moves toward production deployment.

## Stronger Source Verification

Answers include document and page references so staff can verify information before responding to funders.

---

# Future Improvements

Possible future improvements include:

* Cloud document storage
* Hybrid keyword + vector search
* Advanced re-ranking
* Conversation history
* Improved document preview
* Document-level filtering
* Role-based access control
* Multi-organization SaaS support
* Support for additional document formats
* Improved scanned-document processing
* Usage and cost monitoring
* Advanced RAG evaluation

---

# Success Criteria

The DocQuery MVP will be considered successful when:

* Users can create accounts and log in.
* Users can upload supported documents.
* Documents are associated with the correct user.
* Documents remain available after the user returns.
* Documents are processed successfully.
* Text is correctly extracted and chunked.
* Embeddings are generated.
* Chunks are stored in ChromaDB.
* Relevant chunks can be retrieved.
* Gemini generates answers using retrieved context.
* Answers include source information.
* The system avoids unsupported answers.
* The complete application works end-to-end.
* The application can be demonstrated successfully.

---

# Development Roadmap

## Phase 1 — Foundation

* GitHub repository setup
* Python environment setup
* Environment variables
* Gemini API setup
* PostgreSQL setup
* Basic FastAPI setup
* Streamlit setup

## Phase 2 — Authentication & Data

* User registration
* User login
* Authentication handling
* User database model
* Document metadata model
* User-document relationship

## Phase 3 — Document Processing

* PDF processing
* Text extraction
* Text cleaning
* Chunking
* Metadata generation
* Embedding generation
* ChromaDB setup

## Phase 4 — RAG Pipeline

* Query embedding
* Vector search
* Top-K retrieval
* Context construction
* Gemini integration
* Grounded generation
* Source citations
* Retrieval evaluation

## Phase 5 — Application

* Streamlit dashboard
* Document upload interface
* Document library
* Question-answer interface
* Source display
* Authentication integration
* API integration
* Error handling
* Testing

## Phase 6 — Delivery

* End-to-end testing
* Deployment
* Documentation
* README completion
* Demo preparation
* Final presentation

---

# Project Status

**Under Development**

DocQuery is being developed as part of:

**Sprint 2 — AI Application Development with RAG**

---

# License

This project is developed for educational and project demonstration purposes.
