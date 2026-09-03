from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models import User, Document
from backend.schemas import UserRegister, UserLogin, QueryRequest
from backend.security import hash_password, verify_password
from backend.auth import create_access_token, verify_access_token

from rag.retriever import retrieve_documents
from rag.generator import generate_answer


app = FastAPI(title="DocQuery API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


@app.get("/")
def root():
    return {"message": "DocQuery API is running"}


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


@app.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    file_path = f"data/uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "File uploaded successfully",
        "document_id": document.id,
        "filename": document.filename
    }


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