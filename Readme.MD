
Sibiraj S
15:21 (2 minutes ago)
to me

# DocQuery

## AI-Powered Document Question Answering using RAG

DocQuery is an AI-powered document question-answering application designed to help **nonprofit organization staff** quickly find reliable information from documents such as **grant guidelines, donor agreements, and impact reports**.

Instead of manually searching through multiple documents, staff can upload documents and ask questions in natural language. DocQuery uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information and **Gemini AI** to generate grounded answers with source references.

---

## Problem Statement

A nonprofit organization holds grant guidelines, donor agreements, and impact reports, but program staff cannot quickly answer funder questions because the relevant clauses are scattered across many documents.

Finding the required information manually can be time-consuming and may lead to missed or incorrect information.

---

## Solution

DocQuery provides a simple interface where nonprofit staff can:

1. Upload organizational documents.
2. Ask questions in natural language.
3. Retrieve relevant information from the uploaded documents.
4. Generate answers using Gemini AI.
5. View the source document and page associated with the answer.

The system is designed to answer questions based on the uploaded documents rather than relying on unsupported information.

---

## How DocQuery Works

```text
                    User
                     |
                     v
              Upload Documents
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
                Embeddings
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
RAG Pipeline
Document Processing
Document
   ↓
Text Extraction
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
Question Answering
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
Key Features
PDF document upload
PDF text extraction
Text cleaning and chunking
Metadata management
Embedding generation
ChromaDB vector storage
Vector similarity search
Top-K retrieval
Gemini AI answer generation
Source and page citations
Grounded responses
"I don't know" fallback
Basic retrieval and answer evaluation
Streamlit interface
FastAPI backend
Example
User Question
What are the reporting requirements for the grant?

DocQuery Response
The organization must submit an annual impact report covering program outcomes and fund utilization.

Source: Grant_Guidelines.pdf — Page 12

Grounded Answers
DocQuery is designed to generate answers using information retrieved from the uploaded documents.

The system should:

Use the retrieved document context.
Avoid unsupported information.
Avoid relying on outside knowledge for document-specific questions.
Provide the source of the retrieved information.
Clearly indicate when sufficient information is not available.
If the answer cannot be found:

I couldn't find enough information in the provided documents to answer this question.

This helps reduce unsupported or hallucinated responses.

Source Citations
Each document chunk contains metadata such as:

{
  "document_name": "Grant_Guidelines.pdf",
  "document_type": "Grant Guidelines",
  "page": 12,
  "section": "Reporting Requirements",
  "chunk_id": "grant_001_12_03"
}
Example:

Answer:
The organization must submit an annual impact report.

Source:
Grant_Guidelines.pdf
Page: 12
Section: Reporting Requirements
Tech Stack
Technology	Purpose
Python	Main programming language
Streamlit	User interface
FastAPI	Backend API
PyPDF	PDF text extraction
LangChain	RAG pipeline orchestration
Gemini API	AI answer generation
Gemini Embeddings	Convert text into vector representations
ChromaDB	Vector database and similarity search
python-dotenv	Environment variable management
Git	Version control
GitHub	Team collaboration
Note: The exact Gemini embedding model will be finalized based on the available Gemini API/model support during implementation.

Data Storage
Uploaded Documents
During the MVP, uploaded PDFs are stored locally:

data/
└── documents/
    ├── grant_guidelines.pdf
    ├── donor_agreement.pdf
    └── impact_report.pdf
Embeddings and Metadata
Document embeddings and associated metadata are stored in:

ChromaDB
API Keys
API credentials are stored in:

.env
The .env file must never be committed to GitHub.

Project Structure
DocQuery/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
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
│   └── generation/
│       ├── llm.py
│       └── prompts.py
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
API Endpoints
POST /upload
Uploads and processes a document.

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
POST /query
Accepts a natural-language question and returns a grounded answer.

Request
{
  "question": "What are the reporting requirements?"
}
Response
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
Setup
1. Clone the Repository
git clone <repository-url>
cd DocQuery
2. Create a Virtual Environment
python -m venv .venv
3. Activate the Virtual Environment
Windows
.venv\Scripts\activate
macOS / Linux
source .venv/bin/activate
4. Install Dependencies
pip install -r requirements.txt
5. Configure Environment Variables
Create a .env file in the project root:

GEMINI_API_KEY=your_api_key
Never commit the .env file to GitHub.

Running the Application
Start FastAPI Backend
uvicorn app.main:app --reload
Start Streamlit Frontend
streamlit run frontend/streamlit_app.py
Team Responsibilities
The project is divided among three team members.

Member	Responsibility
Member 1	Streamlit / Frontend
Member 2	FastAPI / Backend
Member 3	RAG / AI / Document Processing
Member 1 — Frontend
Streamlit interface
Document upload
Question input
Answer display
Source display
Member 2 — Backend
FastAPI setup
/upload endpoint
/query endpoint
API integration
Error handling
Member 3 — RAG / AI
PDF processing
Text extraction
Text cleaning
Chunking
Metadata
Embeddings
ChromaDB
Retrieval
Gemini integration
Prompt design
Evaluation
DocQuery will be evaluated at both the retrieval and answer levels.

Retrieval Evaluation
Recall@K
Precision@K
Answer Evaluation
Correctness
Groundedness
Citation accuracy
Appropriate "I don't know" responses
Example Evaluation Questions
Question	Expected Source
What are the reporting requirements?	Grant Guidelines
What expenses are eligible?	Grant Guidelines
When is the report due?	Donor Agreement
What outcomes were achieved?	Impact Report
Scope
In Scope
Document upload
PDF processing
Text extraction
Text cleaning
Document chunking
Metadata management
Embedding generation
ChromaDB vector database
Vector similarity search
Top-K retrieval
RAG-based question answering
Gemini AI integration
Grounded responses
Source citations
"I don't know" fallback
Streamlit interface
FastAPI backend
Basic evaluation
Deployment
Out of Scope
Mobile application
Voice assistant
LLM fine-tuning
Training a custom embedding model
Multi-organization SaaS
Advanced authentication and SSO
Payment integration
WhatsApp integration
Complex autonomous agent workflows
Custom model training
Improvements from the Initial Approach
The initial RAG architecture is retained, while a few changes were made to keep the project focused and practical.

Gemini instead of OpenAI
Gemini is used for answer generation and the planned embedding layer, allowing the team to work primarily with one AI ecosystem and simplify API management.

No PostgreSQL for MVP
PostgreSQL is not required because the MVP does not need user accounts, roles, payments, or complex structured application data.

No Supabase Storage
Documents are stored locally during the MVP. Cloud storage can be added later if the project moves toward production deployment.

No Authentication
Login and role management are outside the core problem being solved. The MVP focuses on document retrieval and question answering.

Streamlit for a Simple Frontend
Streamlit provides a fast way to build the document upload and question-answer interface, allowing the team to focus more effort on the RAG pipeline.

Stronger Source Verification
Answers include document and page references so staff can verify information before responding to funders.

Future Improvements
Hybrid keyword + vector search
Advanced re-ranking
Conversation history
Improved document preview
Document-level filtering
Authentication and access control
Cloud document storage
Support for additional document formats
Improved scanned-document processing
Usage and cost monitoring
Advanced RAG evaluation
Success Criteria
The DocQuery MVP will be considered successful when:

 Users can upload supported documents.
 Documents are processed successfully.
 Text is correctly extracted and chunked.
 Embeddings are generated.
 Chunks are stored in ChromaDB.
 Relevant chunks can be retrieved.
 Gemini generates answers using retrieved context.
 Answers include source information.
 The system avoids unsupported answers.
 The complete application works end-to-end.
 The application can be demonstrated successfully.
Development Roadmap
Phase 1 — Foundation
 GitHub repository setup
 Python environment setup
 Environment variables
 Gemini API setup
 Basic document loading
Phase 2 — Document Processing
 PDF processing
 Text extraction
 Text cleaning
 Chunking
 Metadata generation
 Embedding generation
 ChromaDB setup
Phase 3 — RAG Pipeline
 Query embedding
 Vector search
 Top-K retrieval
 Context construction
 Gemini integration
 Grounded generation
 Source citations
 Retrieval evaluation
Phase 4 — Application
 FastAPI backend
 /upload endpoint
 /query endpoint
 Streamlit interface
 Document upload interface
 Question-answer interface
 Source display
 Error handling
 Testing
Phase 5 — Delivery
 End-to-end testing
 Deployment
 Documentation
 README completion
 Demo preparation
 Final presentation
Project Status
Under Development

DocQuery is being developed as part of:

Sprint 2 — AI Application Development with RAG

License
This project is developed for educational and project demonstration purposes.