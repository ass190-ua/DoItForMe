from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency, require_authenticated_user
from app.core.response import success_response
from app.schemas.proposals import ProposalCreateRequest, ProposalResponse
from app.services.proposal_service import ProposalService


router = APIRouter()


@router.post(
    "/{task_id}",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a proposal for a task",
)
async def create_proposal(
    task_id: UUID,
    data: ProposalCreateRequest,
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = ProposalService(session)
    proposal = await service.create_proposal(current_user, task_id, data)
    payload, status_code = success_response(
        {"proposal": proposal.model_dump(mode="json")},
        status_code=status.HTTP_201_CREATED,
    )
    return JSONResponse(status_code=status_code, content=payload)


@router.post(
    "/{proposal_id}/accept",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept a proposal as the task creator",
)
async def accept_proposal(
    proposal_id: UUID,
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = ProposalService(session)
    proposal = await service.accept_proposal(current_user, proposal_id)
    payload, status_code = success_response(
        {"proposal": proposal.model_dump(mode="json")},
        status_code=status.HTTP_200_OK,
    )
    return JSONResponse(status_code=status_code, content=payload)
