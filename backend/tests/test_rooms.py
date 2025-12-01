"""
Unit tests for room endpoints.

Tests cover:
- Room creation
- Room retrieval
- Room deletion
- Error handling
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_room():
    """Test successful room creation."""
    response = client.post("/rooms", json={"language": "python"})
    
    assert response.status_code == 201
    data = response.json()
    
    assert "roomId" in data
    assert data["language"] == "python"
    assert "code" in data
    assert "created_at" in data

def test_create_room_default_language():
    """Test room creation with default language."""
    response = client.post("/rooms", json={})
    
    assert response.status_code == 201
    data = response.json()
    assert data["language"] == "python"

def test_get_room():
    """Test retrieving an existing room."""
    # Create room first
    create_response = client.post("/rooms", json={"language": "python"})
    room_id = create_response.json()["roomId"]
    
    # Get room
    response = client.get(f"/rooms/{room_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["roomId"] == room_id

def test_get_nonexistent_room():
    """Test retrieving a room that doesn't exist."""
    response = client.get("/rooms/nonexistent")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_delete_room():
    """Test deleting an existing room."""
    # Create room first
    create_response = client.post("/rooms", json={"language": "python"})
    room_id = create_response.json()["roomId"]
    
    # Delete room
    response = client.delete(f"/rooms/{room_id}")
    
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/rooms/{room_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_room():
    """Test deleting a room that doesn't exist."""
    response = client.delete("/rooms/nonexistent")
    
    assert response.status_code == 404