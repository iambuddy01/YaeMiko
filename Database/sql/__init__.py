from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from Mikobot import DB_URI
from Mikobot import LOGGER as log

# Base must be defined first
BASE = declarative_base()

# Fix Heroku postgres:// → postgresql://
if DB_URI and DB_URI.startswith("postgres://"):
    DB_URI = DB_URI.replace("postgres://", "postgresql://", 1)


def start() -> scoped_session:
    log.info("[PostgreSQL] Connecting to database......")

    engine = create_engine(
        DB_URI,
        client_encoding="utf8",
        pool_pre_ping=True,
        connect_args={"sslmode": "require"}  # 🔴 REQUIRED for Heroku
    )

    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)

    return scoped_session(
        sessionmaker(bind=engine, autoflush=False)
    )


try:
    SESSION = start()
    log.info("[PostgreSQL] Connection successful, session started.")
except Exception as e:
    log.exception(f"[PostgreSQL] Failed to connect due to {e}")
    exit(1)

