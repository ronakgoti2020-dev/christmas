import os
import sys
from collections.abc import Generator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production-use"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SMTP_HOST"] = ""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

from app.database import Base, get_db
from app.main import app
from app import models  # noqa: F401

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=True)
Base.metadata.create_all(bind=engine)


def override_db() -> Generator:
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db


@pytest.fixture()
def client() -> TestClient:
    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
    return TestClient(app)


def auth_header(client: TestClient, email: str, name: str = "User") -> dict[str, str]:
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": name,
            "email": email,
            "password": "Secret123",
            "country": "India",
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
