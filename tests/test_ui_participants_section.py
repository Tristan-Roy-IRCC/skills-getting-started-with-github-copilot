from pathlib import Path

from fastapi.testclient import TestClient

from src.app import app


def test_activity_cards_include_participants_section():
    js = Path("src/static/app.js").read_text()

    assert "participants-list" in js
    assert "details.participants" in js


def test_signup_success_refreshes_activity_cards_without_reload():
    js = Path("src/static/app.js").read_text()

    assert "await fetchActivities()" in js


def test_delete_signup_endpoint_unregisters_participant():
    client = TestClient(app)
    email = "student@example.edu"

    post_response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert post_response.status_code == 200

    delete_response = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert delete_response.status_code == 200

    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]
