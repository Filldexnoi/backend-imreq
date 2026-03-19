from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # test connection before use (detect stale connections)
    pool_recycle=300,        # recycle connections every 5 minutes
    pool_timeout=30,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_with_retry(max_attempts: int = 10, base_delay: float = 2.0):
    """
    Open a DB session with exponential backoff retry.
    Handles 'database system is in recovery mode' and other transient errors.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            db = SessionLocal()
            # Probe the connection — forces pool_pre_ping to actually verify
            db.execute(text("SELECT 1"))
            return db
        except Exception as e:
            err = str(e)
            if attempt < max_attempts and ("recovery mode" in err or "could not connect" in err or "connection refused" in err):
                delay = base_delay * (2 ** (attempt - 1))  # 2, 4, 8, 16...
                logger.warning(f"DB not ready (attempt {attempt}/{max_attempts}): {err[:120]}. Retrying in {delay:.0f}s...")
                time.sleep(delay)
            else:
                raise