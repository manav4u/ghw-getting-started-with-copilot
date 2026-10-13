"""Backend tests for the activities API, using the Arrange-Act-Assert pattern."""
import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_name in response.json() or len(response.json()) > 0


def test_signup_adds_participant():
    # Arrange
    name = next(iter(activities))
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[name]["participants"]


def test_signup_duplicate_is_rejected():
    # Arrange
    name = next(iter(activities))
    email = activities[name]["participants"][0] if activities[name]["participants"] else "dup@mergington.edu"
    if email not in activities[name]["participants"]:
        activities[name]["participants"].append(email)

    # Act
    response = client.post(f"/activities/{name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400


def test_signup_unknown_activity_returns_404():
    # Arrange
    name = "Does Not Exist"

    # Act
    response = client.post(f"/activities/{name}/signup", params={"email": "a@mergington.edu"})

    # Assert
    assert response.status_code == 404


def test_unregister_removes_participant():
    # Arrange
    name = next(iter(activities))
    email = "leaving@mergington.edu"
    activities[name]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[name]["participants"]


def test_unregister_missing_participant_returns_400():
    # Arrange
    name = next(iter(activities))

    # Act
    response = client.delete(f"/activities/{name}/unregister", params={"email": "nobody@mergington.edu"})

    # Assert
    assert response.status_code == 400
