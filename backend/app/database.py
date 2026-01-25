from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ecom_user:ecom_pass@localhost:5432/ecom_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Updated on 2026-01-26 by Anwar

# Updated on 2026-03-07 by Anwar
change 13
change 7
change 19
change 24
change 8
change 8
change 27
change 3
change 23
