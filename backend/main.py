from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pypdf import PdfReader

from database.connection import SessionLocal
from database.models import User, Document
from backend.schemas import UserRegister, UserLogin, QueryRequest
from backend.security import hash_password, verify_password
from backend.auth import create_access_token, verify_access_token
from backend.services.document_processor import process_document

from rag.retriever import retrieve_documents
from rag.generator import generate_answer


app = FastAPI(title="DocQuery API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# --------------------------------------------------
# File Upload Configuration
# --------------------------------------------------

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# --------------------------------------------------
# Database Dependency
# --------------------------------------------------

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# --------------------------------------------------
# Authentication
# --------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "DocQuery API is running"
    }


# --------------------------------------------------
# User Registration
# --------------------------------------------------

@app.post("/register")
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


# --------------------------------------------------
# User Login
# --------------------------------------------------

@app.post("/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"user_id": user.id}
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }


# --------------------------------------------------
# Current User
# --------------------------------------------------

@app.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }


# --------------------------------------------------
# PDF Upload
# --------------------------------------------------

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ----------------------------------------------
    # 1. Check whether a file was selected
    # ----------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    original_filename = Path(file.filename).name

    # ----------------------------------------------
    # 2. Validate file extension
    # ----------------------------------------------

    if Path(original_filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # ----------------------------------------------
    # 3. Validate MIME type
    # ----------------------------------------------

    allowed_content_types = {
        "application/pdf",
        "application/x-pdf"
    }

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PDF file."
        )

    # ----------------------------------------------
    # 4. Read uploaded file
    # ----------------------------------------------

    content = await file.read()

    # ----------------------------------------------
    # 5. Validate file size
    # ----------------------------------------------

    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must not exceed 10 MB"
        )

    # ----------------------------------------------
    # 6. Validate PDF file signature
    # ----------------------------------------------

    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    # ----------------------------------------------
    # 7. Generate unique filename
    # ----------------------------------------------

    unique_filename = f"{uuid4().hex}_{original_filename}"

    file_path = UPLOAD_DIR / unique_filename

    # ----------------------------------------------
    # 8. Save the file temporarily
    # ----------------------------------------------

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # ------------------------------------------
        # 9. Verify that PDF is readable
        # ------------------------------------------

        reader = PdfReader(str(file_path))

        page_count = len(reader.pages)

        if page_count == 0:
            raise ValueError("PDF contains no pages")

    except Exception:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid or readable PDF"
        )

    # ----------------------------------------------
    # 10. Create database record
    # ----------------------------------------------

    document = Document(
        user_id=current_user.id,
        filename=original_filename,
        file_path=str(file_path),
        status="Processing"
    )

    db.add(document)
    db.commit()
    db.refresh(document)


    # ----------------------------------------------
    # 11. Return upload response
    # ----------------------------------------------

    try:
        process_document(
            str(file_path),
            original_filename
        )

        document.status = "Ready"
        db.commit()

    except Exception:
        document.status = "Failed"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        )

    # ----------------------------------------------
    # 12. Return upload response
    # ----------------------------------------------

    return {
        "message": "PDF uploaded and processed successfully",
        "document_id": document.id,
        "filename": original_filename,
        "pages": page_count,
        "status": document.status,
        "file_path": str(file_path)
    }

# --------------------------------------------------
# Document Query
# --------------------------------------------------

@app.post("/query")
def query_document(
    query_data: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    retrieved_documents = retrieve_documents(
        query_data.question,
        top_k=5
    )

    answer = generate_answer(
        query_data.question,
        retrieved_documents
    )

    sources = []
    seen_sources = set()

    for document in retrieved_documents:
        metadata = document["metadata"]

        source = (
            metadata.get("document_name"),
            metadata.get("page")
        )

        if source not in seen_sources:
            seen_sources.add(source)

            sources.append({
                "document": source[0],
                "page": source[1]
            })

    return {
        "user_id": current_user.id,
        "question": query_data.question,
        "answer": answer,
        "sources": sources
    }
