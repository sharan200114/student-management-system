from flask_jwt_extended import create_access_token

import pytest

from app import app


@pytest.fixture
def client():

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# Test 1: API home
def test_api_home(client):

    response = client.get("/api")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True


# Test 2: Student API requires authentication
def test_students_require_authentication(client):

    response = client.get("/api/students")

    assert response.status_code == 401


# Test 3: Student creation requires valid input

def test_create_student_invalid_data(client):

    # Generate a valid JWT token
    with client.application.app_context():
        access_token = create_access_token(
            identity="1"
        )

    # Send invalid student data with authentication
    response = client.post(
        "/api/students",
        json={},
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    # Verify validation response
    assert response.status_code == 400



# Test 5: Invalid student ID
def test_student_id_must_be_integer(client):

    response = client.get("/api/students/abc")

    assert response.status_code == 404

# Test 5: Login Credential
def test_login_requires_credentials(client):

    response = client.post(
        "/api/auth/login",
        json={}
    )

    assert response.status_code == 400
