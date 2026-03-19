from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1 import auth as auth_router_module
from app.api.v1 import users as users_router_module
from app.core.response import success_response


router = APIRouter()
router.include_router(auth_router_module.router, prefix="/auth", tags=["auth"])
router.include_router(users_router_module.router, prefix="/users", tags=["users"])


@router.get("", summary="API v1 root")
async def api_root() -> JSONResponse:
    payload, status_code = success_response({"message": "DoItForMe API v1"})
    return JSONResponse(status_code=status_code, content=payload)
