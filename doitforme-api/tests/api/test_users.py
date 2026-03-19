import pytest
from fastapi.testclient import TestClient

from app.api.deps import db_session_dependency, require_authenticated_user
from app.main import app as fastapi_app


class DummySession:
    pass


def override_authenticated_user():
    return {
        "sub": "00000000-0000-0000-0000-000000000001",
        "email": "me@example.com",
        "role": "poster",
        "jti": "session-jti",
    }


async def override_db_session():
    yield DummySession()


class TestUsersAuthValidation:
    client = TestClient(fastapi_app)

    def test_get_my_profile_requires_authorization(self):
        response = self.client.get("/api/v1/users/me")

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "AUTHENTICATION_REQUIRED"

    def test_update_my_profile_requires_authorization(self):
        response = self.client.put(
            "/api/v1/users/me",
            json={
                "name": "Updated User",
                "latitude": 41.3874,
                "longitude": 2.1686,
            },
        )

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "AUTHENTICATION_REQUIRED"

    def test_update_my_profile_rejects_invalid_payload(self):
        fastapi_app.dependency_overrides[require_authenticated_user] = (
            override_authenticated_user
        )
        fastapi_app.dependency_overrides[db_session_dependency] = override_db_session

        try:
            response = self.client.put(
                "/api/v1/users/me",
                json={
                    "name": "",
                    "latitude": 120,
                    "longitude": 2.1686,
                    "role": "admin",
                },
            )
        finally:
            fastapi_app.dependency_overrides.clear()

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"


class TestPublicProfileValidation:
    client = TestClient(fastapi_app)

    def test_get_public_profile_rejects_invalid_uuid(self):
        response = self.client.get("/api/v1/users/not-a-uuid")

        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.skip(reason="requires live PostgreSQL database")
def test_get_my_profile_success():
    pass


@pytest.mark.skip(reason="requires live PostgreSQL database")
def test_update_my_profile_success():
    pass


@pytest.mark.skip(reason="requires live PostgreSQL database")
def test_get_public_profile_success():
    pass


@pytest.mark.skip(reason="requires live PostgreSQL database")
def test_get_public_profile_not_found():
    pass
