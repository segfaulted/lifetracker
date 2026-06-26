from sqlmodel import SQLModel, create_engine, Session

import os

DATABASE_FILE = os.getenv("DATABASE_FILE", "./tracker.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

def get_db():
    with Session(engine) as session:
        yield session
