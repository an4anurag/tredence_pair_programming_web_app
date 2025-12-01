"""
Unit tests for autocomplete endpoint.

Tests cover:
- Basic autocomplete requests
- Different code patterns
- Error handling
- Edge cases
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_autocomplete_print_statement():
    """Test autocomplete for print statement."""
    response = client.post(
        "/autocomplete",
        json={
            "code": "print(",
            "cursorPosition": 6,
            "language": "python"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "suggestion" in data
    assert "confidence" in data
    assert "type" in data
    assert 0.0 <= data["confidence"] <= 1.0

def test_autocomplete_function_definition():
    """Test autocomplete for function definition."""
    response = client.post(
        "/autocomplete",
        json={
            "code": "def hello():\n    ",
            "cursorPosition": 17,
            "language": "python"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "suggestion" in data

def test_autocomplete_invalid_cursor_position():
    """Test autocomplete with invalid cursor position."""
    response = client.post(
        "/autocomplete",
        json={
            "code": "print('hello')",
            "cursorPosition": 100,  # Beyond code length
            "language": "python"
        }
    )
    
    assert response.status_code == 400

def test_autocomplete_empty_code():
    """Test autocomplete with empty code."""
    response = client.post(
        "/autocomplete",
        json={
            "code": "",
            "cursorPosition": 0,
            "language": "python"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "suggestion" in data

def test_autocomplete_javascript():
    """Test autocomplete for JavaScript."""
    response = client.post(
        "/autocomplete",
        json={
            "code": "console.log(",
            "cursorPosition": 12,
            "language": "javascript"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "suggestion" in data

def test_autocomplete_response_structure():
    """Test that autocomplete response has correct structure."""
    response = client.post(
        "/autocomplete",
        json={
            "code": "x = ",
            "cursorPosition": 4,
            "language": "python"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check all required fields
    assert "suggestion" in data
    assert "confidence" in data
    assert "type" in data
    
    # Check types
    assert isinstance(data["suggestion"], str)
    assert isinstance(data["confidence"], float)
    assert isinstance(data["type"], str)