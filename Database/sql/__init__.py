from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from Mikobot import DB_URI
from Mikobot import LOGGER as log
import sys


BASE = declarative_base()
SESSION = None


def normalize_db_uri(uri: str) -> str:
    if not uri:
        raise ValueError("DB_URI is empty or not set")

    uri = uri.strip()

    # Heroku legacy fix
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    # Basic sanity check
    if not uri.startswith("postgresql://"):
        raise ValueError(f"Invalid DB_URI format: {uri}")

    return uri


def start() -> scoped_session:
    global DB_URI

    DB_URI = normalize_db_uri(DB_URI)

    log.info("[PostgreSQL] Connecting to database...")

    engine = create_engine(
        DB_URI,
        pool_pre_ping=True,
        client_encoding="utf8",
    )

    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)

    return scoped_session(
        sessionmaker(bind=engine, autoflush=False, autocommit=False)
    )


try:
    SESSION = start()
    log.info("[PostgreSQL] Connection successful, session started.")
except Exception as e:
    log.exception(f"[PostgreSQL] Failed to connect: {e}")
    sys.exit(1)

