from app.core.config import Settings, get_settings
from app.db.session import SessionLocal


def test_settings_and_session_factory_are_available():
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.api_v1_prefix == "/api/v1"
    assert SessionLocal is not None
