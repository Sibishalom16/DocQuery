from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models import User
from backend.schemas import UserRegister
from backend.security import hash_password

app = FastAPI(title="DocQuery API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "DocQuery API is running"}


@app.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):

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