import random

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import get_db
from app.models import Base, Product, Score
from app.main import app

# In-memory SQLite for tests — StaticPool ensures all connections share the same database
_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


@pytest.fixture()
def db():
    """Create tables, yield a session, then drop tables."""
    Base.metadata.create_all(bind=_test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture()
def client(db):
    """FastAPI TestClient with the get_db dependency overridden to use the test session."""

    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_product(db):
    """Create and return a persisted Product."""
    product = Product(name="Test Product", product_type="Product", is_active=True, is_assessed=True)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture()
def sample_score(db, sample_product):
    """Create and return a Score with random capability values (1-4)."""
    rng = random.Random(42)  # deterministic seed
    kwargs = {}
    from app.models.score import ALL_CAPABILITY_FIELDS

    for field in ALL_CAPABILITY_FIELDS:
        kwargs[field] = rng.randint(1, 4)

    score = Score(product_id=sample_product.id, latest=True, **kwargs)
    db.add(score)
    db.commit()
    db.refresh(score)
    return score
