import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_success():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_nonexistent_activity_returns_404():
    response = client.post("/activities/Nonexistent%20Club/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student_returns_400():
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_success():
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    response = client.delete(f"/activities/{quote(activity_name)}/participants?email={quote(email)}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_not_found_returns_404():
    activity_name = "Chess Club"
    email = "missingstudent@mergington.edu"
    response = client.delete(f"/activities/{quote(activity_name)}/participants?email={quote(email)}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
