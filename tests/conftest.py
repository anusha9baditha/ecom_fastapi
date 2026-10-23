import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, get_db
from main import app
from models import User
from utils.security import hash_password

TEST_ENGINE = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=TEST_ENGINE, autoflush=False, autocommit=False)

@pytest.fixture()
def db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=TEST_ENGINE)

@pytest.fixture()
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture()
def make_user(db):
    def _make_user(role="customer", email=None):
        user = User(name="Test User", email=email or f"{role}@example.com", hashed_password=hash_password("TestPass123!"), role=role, is_active=True)
        db.add(user); db.commit(); db.refresh(user)
        return user
    return _make_user

@pytest.fixture()
def auth_headers(client):
    def _headers(email, password="TestPass123!"):
        response = client.post("/auth/login", json={"email": email, "password": password})
        assert response.status_code == 200, response.text
        return {"Authorization": f"Bearer {response.json()['access_token']}"}
    return _headers
