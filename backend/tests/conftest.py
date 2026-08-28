import os

# Must be set BEFORE any app module is imported, since Settings are cached
# via lru_cache and the app's lifespan hook touches this engine on startup.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # unused in tests (cache calls are mocked below)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.database import Base, get_db

# Isolated in-memory DB per test session — no dependency on real Postgres.
# StaticPool keeps a single shared connection alive across threads, which
# matters because TestClient's ASGI transport can execute the app on a
# different thread than the test itself (each thread would otherwise see
# its own empty in-memory database).
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class _FakeRedis:
    """Minimal in-memory stand-in for redis.Redis, used so tests don't
    require a running Redis server. Only implements what our app needs."""

    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value, ex=None):
        self._store[key] = value

    def delete(self, key):
        self._store.pop(key, None)


@pytest.fixture(autouse=True)
def fake_redis():
    with patch("app.redis_client.redis_client", _FakeRedis()):
        yield


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
