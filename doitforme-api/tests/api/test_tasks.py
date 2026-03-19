import pytest
from fastapi.testclient import TestClient

from app.api.deps import db_session_dependency, require_authenticated_user
from app.main import app as fastapi_app


class DummySession:
    pass


def override_poster_user():
    return {
        "sub": "00000000-0000-0000-0000-000000000010",
        "email": "poster@example.com",
        "role": "poster",
        "jti": "task-jti",
    }


def override_performer_user():
    return {
        "sub": "00000000-0000-0000-0000-000000000011",
        "email": "performer@example.com",
        "role": "performer",
        "jti": "task-jti",
    }


async def override_db_session():
    yield DummySession()


class TestTaskAuthValidation:
    client = TestClient(fastapi_app)

    def test_create_task_requires_authorization(self):
        response = self.client.post(
            "/api/v1/tasks",
            json={
                "title": "Pick up dry cleaning",
                "description": "Get my suit from the cleaner",
                "location": {"latitude": 40.7128, "longitude": -74.0060},
                "initial_price": 15.00,
            },
        )

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "AUTHENTICATION_REQUIRED"

    def test_create_task_rejects_invalid_payload(self):
        fastapi_app.dependency_overrides[require_authenticated_user] = (
            override_poster_user
        )
        fastapi_app.dependency_overrides[db_session_dependency] = override_db_session

        try:
            response = self.client.post(
                "/api/v1/tasks",
                json={
                    "title": "",
                    "description": "Get my suit from the cleaner",
                    "location": {"latitude": 120, "longitude": -74.0060},
                    "initial_price": -1,
                },
            )
        finally:
            fastapi_app.dependency_overrides.clear()

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_create_task_rejects_non_poster_role(self):
        fastapi_app.dependency_overrides[require_authenticated_user] = (
            override_performer_user
        )
        fastapi_app.dependency_overrides[db_session_dependency] = override_db_session

        try:
            response = self.client.post(
                "/api/v1/tasks",
                json={
                    "title": "Pick up dry cleaning",
                    "description": "Get my suit from the cleaner",
                    "location": {"latitude": 40.7128, "longitude": -74.0060},
                    "initial_price": 15.00,
                },
            )
        finally:
            fastapi_app.dependency_overrides.clear()

        assert response.status_code == 403
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "FORBIDDEN_ROLE"


@pytest.mark.skip(reason="requires live PostgreSQL database")
def test_create_task_success():
    pass
