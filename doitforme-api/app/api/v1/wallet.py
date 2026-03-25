from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency, require_authenticated_user
from app.core.response import success_response
from app.schemas.wallet import DepositRequest
from app.services.wallet_service import WalletService

router = APIRouter()


@router.get("/me", summary="Get my wallet balance and transaction history")
async def get_my_wallet(
    current_user: dict = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = WalletService(session)
    user_id = UUID(current_user["sub"])
    wallet = await service.get_wallet(user_id)
    payload, status_code = success_response({"wallet": wallet.model_dump(mode="json")})
    return JSONResponse(status_code=status_code, content=payload)


@router.post("/deposit", summary="Deposit funds into wallet (simulated)")
async def deposit_funds(
    data: DepositRequest,
    current_user: dict = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = WalletService(session)
    user_id = UUID(current_user["sub"])
    wallet = await service.deposit(user_id, data)
    payload, status_code = success_response({"wallet": wallet.model_dump(mode="json")})
    return JSONResponse(status_code=status_code, content=payload)
