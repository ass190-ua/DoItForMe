from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session_dependency, require_authenticated_user
from app.core.response import success_response
from app.schemas.reviews import ReviewCreate, ReviewCreateRequest, ReviewResponse
from app.services.review_service import ReviewService

router = APIRouter()

@router.post(
    "/{task_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new review",
)
async def create_review(
    task_id: UUID,
    data: ReviewCreate,
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = ReviewService(session)
    # We map task_id from path to the service data
    from app.schemas.reviews import ReviewCreateRequest
    request_data = ReviewCreateRequest(
        task_id=task_id,
        reviewee_id=data.reviewee_id,
        rating=data.rating,
        comment=data.comment
    )
    review = await service.create_review(current_user, request_data)
    payload, status_code = success_response(
        {"review": review.model_dump(mode="json")},
        status_code=status.HTTP_201_CREATED,
    )
    return JSONResponse(status_code=status_code, content=payload)


@router.get(
    "/me",
    summary="Get my received reviews",
)
async def get_my_reviews(
    limit: int = 20,
    offset: int = 0,
    current_user: dict[str, str] = Depends(require_authenticated_user),
    session: AsyncSession = Depends(db_session_dependency),
) -> JSONResponse:
    service = ReviewService(session)
    user_id = UUID(current_user["sub"])
    reviews = await service.get_user_reviews(user_id, limit=limit, offset=offset)
    payload, status_code = success_response(
        {"reviews": [r.model_dump(mode="json") for r in reviews]}
    )
    return JSONResponse(status_code=status_code, content=payload)
