from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1 import admin, auth, proposals, reviews, tasks, users, messages, wallet, uploads, user_dashboard
from app.core.response import success_response


router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(proposals.router, prefix="/proposals", tags=["proposals"])
router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(user_dashboard.router, prefix="/users/me", tags=["dashboard"])
router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
router.include_router(messages.router, prefix="/tasks", tags=["messages"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])


@router.get("", summary="API v1 root")
async def api_root() -> JSONResponse:
    payload, status_code = success_response({"message": "DoItForMe API v1"})
    return JSONResponse(status_code=status_code, content=payload)
