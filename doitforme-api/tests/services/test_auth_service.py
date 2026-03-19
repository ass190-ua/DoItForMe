from app.services.auth_service import AuthService


def test_auth_service_initializes_with_session_stub():
    service = AuthService(session=None)  # type: ignore[arg-type]

    assert service.session is None
    assert service.user_repository is not None
