from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

# pool_pre_ping avoids stale-connection errors in long-lived containers.
# SQLite (used in tests / local quick-start) doesn't support pool_size/max_overflow.
_engine_kwargs = {"pool_pre_ping": True}
if not settings.DATABASE_URL.startswith("sqlite"):
    _engine_kwargs.update(pool_size=10, max_overflow=20)
else:
    from sqlalchemy.pool import StaticPool
    _engine_kwargs.update(connect_args={"check_same_thread": False}, poolclass=StaticPool)

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
