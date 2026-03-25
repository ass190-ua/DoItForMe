import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole

@pytest.mark.asyncio
async def test_minimal_user_creation(session: AsyncSession):
    from app.core.config import get_settings
    print(f"DEBUG: DATABASE URL IN TEST: {get_settings().database_url}")
    suffix = str(uuid4())[:8]

    u = User(email=f"simple_{suffix}@x.com", password_hash="h", name="S", role=UserRole.POSTER)
    print(f"DEBUG: User object created. ID before add: {u.user_id}")
    session.add(u)
    print(f"DEBUG: User object added. ID before commit: {u.user_id}")
    try:
        await session.commit()
    except Exception as e:
        print(f"DEBUG: FAILED COMMIT! Error: {e}")
        # Try to print more detail if it is a DB error
        if hasattr(e, 'orig'):
            print(f"DEBUG: DB Error Detail: {e.orig}")
        raise
    print(f"DEBUG: Success! ID after commit: {u.user_id}")
    assert u.user_id is not None
