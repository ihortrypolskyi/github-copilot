"""
Backend API tests for Mergington High School Activities application.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and initial state
- Act: Execute the endpoint call
- Assert: Verify response status, message, and state changes
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    # Arrange: Set up initial state
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other artistic mediums",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in plays and learn theater skills",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and learn about scientific concepts",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": []
        }
    }
    
    # Clear and reset the activities dictionary
    activities.clear()
    activities.update(initial_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_activity_count
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_includes_participants(self, client):
        """Test that GET /activities includes participant lists."""
        # Arrange
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["Chess Club"]["participants"] == expected_chess_participants
    
    def test_get_activities_includes_max_participants(self, client):
        """Test that GET /activities includes max_participants field."""
        # Arrange
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["Chess Club"]["max_participants"] == 12
        assert data["Programming Class"]["max_participants"] == 20


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant_success(self, client):
        """Test successfully signing up a new participant."""
        # Arrange
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]
        assert email in activities[activity_name]["participants"]
    
    def test_signup_participant_already_registered(self, client):
        """Test that signing up a participant twice returns an error."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test that signing up for a nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "alex@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_multiple_participants(self, client):
        """Test that multiple participants can sign up for the same activity."""
        # Arrange
        activity_name = "Soccer Club"
        email1 = "alice@mergington.edu"
        email2 = "bob@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email1}",
            json={}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={email2}",
            json={}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_unregister_existing_participant(self, client):
        """Test successfully unregistering a participant."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test that unregistering a nonexistent participant returns 404."""
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test that unregistering from a nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_multiple_participants(self, client):
        """Test unregistering multiple participants."""
        # Arrange
        activity_name = "Gym Class"
        email1 = "john@mergington.edu"
        email2 = "olivia@mergington.edu"
        
        # Act
        response1 = client.delete(
            f"/activities/{activity_name}/participants?email={email1}"
        )
        response2 = client.delete(
            f"/activities/{activity_name}/participants?email={email2}"
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 not in activities[activity_name]["participants"]
        assert email2 not in activities[activity_name]["participants"]


class TestIntegrationFlow:
    """Integration tests for signup and unregister flows."""
    
    def test_signup_then_unregister_flow(self, client):
        """Test a complete flow: signup, verify, and unregister."""
        # Arrange
        activity_name = "Art Club"
        email = "artist@mergington.edu"
        
        # Act: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        
        # Assert: Signup successful
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Act: Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        
        # Assert: Unregister successful
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    
    def test_signup_and_unregister_updates_availability(self, client):
        """Test that signup and unregister update available spots."""
        # Arrange
        activity_name = "Drama Club"
        email = "actor@mergington.edu"
        initial_participants = len(activities[activity_name]["participants"])
        
        # Act: Sign up
        client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        
        # Assert: Participant count increased
        after_signup = len(activities[activity_name]["participants"])
        assert after_signup == initial_participants + 1
        
        # Act: Unregister
        client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        
        # Assert: Participant count back to initial
        after_unregister = len(activities[activity_name]["participants"])
        assert after_unregister == initial_participants
