import pytest
from fastapi.testclient import TestClient
from src.api.routes.form import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns correct message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "NomadAI Form API is running!"}

def test_travel_plan_endpoint():
    """Test the travel plan endpoint with valid data"""
    test_data = {
        "origin": "New York",
        "destination": "Paris",
        "startDate": "2024-06-01",
        "endDate": "2024-06-07",
        "strictDates": "yes",
        "budget": "5000",
        "people": "2",
        "travelMode": "plane",
        "activities": ["sightseeing", "food", "culture"],
        "visitedBefore": "no",
        "hotelPreference": "luxury"
    }
    
    response = client.post("/api/travel-plan", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "timestamp" in data
    assert "data" in data

def test_get_travel_forms_endpoint():
    """Test the get travel forms endpoint"""
    response = client.get("/api/travel-forms")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "total_entries" in data
    assert "data" in data
