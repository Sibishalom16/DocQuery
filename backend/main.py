from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database.connection import SessionLocal

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