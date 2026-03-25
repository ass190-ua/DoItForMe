from uuid import UUID
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.proposal import Proposal


class ProposalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, proposal: Proposal) -> Proposal:
        self.session.add(proposal)
        await self.session.flush()
        await self.session.refresh(proposal)
        return proposal

    async def get_by_id(self, proposal_id: UUID) -> Proposal | None:
        result = await self.session.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        return result.scalar_one_or_none()

    async def get_by_task_id(self, task_id: UUID) -> Sequence[Proposal]:
        result = await self.session.execute(
            select(Proposal).where(Proposal.task_id == task_id).order_by(Proposal.created_at.desc())
        )
        return result.scalars().all()

    async def update(self, proposal: Proposal) -> Proposal:
        await self.session.flush()
        await self.session.refresh(proposal)
        return proposal
