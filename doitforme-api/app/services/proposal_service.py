from uuid import UUID
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.proposal import Proposal, ProposalStatus
from app.models.task import TaskStatus
from app.models.transaction import Transaction, TransactionType
from app.repositories.proposal_repository import ProposalRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.proposals import ProposalCreateRequest, ProposalPublic


class ProposalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.proposal_repository = ProposalRepository(session)
        self.task_repository = TaskRepository(session)
        self.user_repository = UserRepository(session)
        self.transaction_repository = TransactionRepository(session)

    async def create_proposal(
        self,
        current_user: dict[str, str],
        task_id: UUID,
        data: ProposalCreateRequest,
    ) -> ProposalPublic:
        user_id = UUID(current_user["sub"])
        
        # Check task exists and is published or negotiating
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise AppException(
                code="NOT_FOUND",
                message="Task not found",
                status_code=404,
            )
            
        if task.status not in (TaskStatus.PUBLISHED, TaskStatus.NEGOTIATING):
            raise AppException(
                code="INVALID_STATE",
                message="Proposals can only be made on published or negotiating tasks",
                status_code=400,
            )
            
        if task.creator_id == user_id:
            raise AppException(
                code="FORBIDDEN",
                message="You cannot propose on your own task",
                status_code=403,
            )

        proposal = Proposal(
            task_id=task_id,
            runner_id=user_id,
            proposed_price=data.proposed_price,
            message=data.message,
            status=ProposalStatus.PENDING,
        )

        created_proposal = await self.proposal_repository.create(proposal)
        
        if task.status == TaskStatus.PUBLISHED:
            task.status = TaskStatus.NEGOTIATING
            await self.task_repository.update(task)
        
        await self.session.commit()
        return ProposalPublic.model_validate(created_proposal)

    async def accept_proposal(
        self,
        current_user: dict[str, str],
        proposal_id: UUID,
    ) -> ProposalPublic:
        user_id = UUID(current_user["sub"])
        
        proposal = await self.proposal_repository.get_by_id(proposal_id)
        if not proposal:
            raise AppException(
                code="NOT_FOUND",
                message="Proposal not found",
                status_code=404,
            )
            
        task = await self.task_repository.get_by_id(proposal.task_id)
        
        if task.creator_id != user_id:
            raise AppException(
                code="FORBIDDEN",
                message="Only the task creator can accept proposals",
                status_code=403,
            )

        if proposal.status != ProposalStatus.PENDING:
            raise AppException(
                code="INVALID_STATE",
                message="Only pending proposals can be accepted",
                status_code=400,
            )

        # --- ESCROW HOLD (atomic, same transaction) ---
        # 1. Lock creator row to prevent concurrent balance modifications
        creator = await self.user_repository.get_for_update(task.creator_id)

        # 2. Validate sufficient funds
        if creator.balance < proposal.proposed_price:
            raise AppException(
                code="INSUFFICIENT_FUNDS",
                message="You do not have enough balance to accept this proposal",
                status_code=400,
            )

        # 3. Deduct from creator balance
        creator.balance -= proposal.proposed_price
        await self.user_repository.update(creator)

        # 4. Record ESCROW_HOLD transaction (negative amount)
        escrow_tx = Transaction(
            user_id=creator.user_id,
            amount=-proposal.proposed_price,
            transaction_type=TransactionType.ESCROW_HOLD,
            task_id=task.task_id,
        )
        await self.transaction_repository.create(escrow_tx)
        # --- END ESCROW HOLD ---

        proposal.status = ProposalStatus.ACCEPTED
        await self.proposal_repository.update(proposal)
        
        task.status = TaskStatus.ACCEPTED
        task.runner_id = proposal.runner_id
        task.accepted_price = proposal.proposed_price
        await self.task_repository.update(task)
        
        # Reject other proposals
        other_proposals = await self.proposal_repository.get_by_task_id(task.task_id)
        for other in other_proposals:
            if other.id != proposal.id and other.status == ProposalStatus.PENDING:
                other.status = ProposalStatus.REJECTED
                await self.proposal_repository.update(other)
        
        await self.session.commit()
        return ProposalPublic.model_validate(proposal)
