import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models  # noqa: F401  # garante que as classes ORM são registradas

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        # antes com o return a func encerrava e nunca fechava a connection, agora com o yeld, ela retorna sem encerrar.
        yield db
    finally:
        db.close()
