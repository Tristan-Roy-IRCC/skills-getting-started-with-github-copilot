import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from src.app import app, activities


# Arrange, Act, Assert pattern for backend FastAPI route tests

def test_get_activities_returns_activity_catalog():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_route_rejects_duplicate_registration():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "backend-duplicate@example.edu"

    # Sign up and confirm registration in the first step.
    first_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert first_response.status_code == 200

    # Act
    duplicate_response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert duplicate_response.status_code == 400
    assert "already signed up" in duplicate_response.json()["detail"].lower()

    # Cleanup shared in-memory state for the test module.
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)


def test_delete_route_unregisters_a_student():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "backend-delete@example.edu"

    # Arrange production state by adding the test email once.
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    delete_response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert delete_response.status_code == 200
    assert delete_response.json()["message"].startswith("Removed")
    assert email not in client.get("/activities").json()[activity_name]["participants"]

    # Cleanup if the call above left the route state altered unexpectedly.
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)
