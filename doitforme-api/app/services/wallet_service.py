from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.transaction import Transaction, TransactionType
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.wallet import DepositRequest, TransactionPublic, WalletResponse


class WalletService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.transaction_repository = TransactionRepository(session)

    async def get_wallet(self, current_user_id: UUID) -> WalletResponse:
        user = await self.user_repository.get_by_id(current_user_id)
        if not user:
            raise AppException(
                code="USER_NOT_FOUND",
                message="User not found",
                status_code=404,
            )

        transactions = await self.transaction_repository.get_by_user_id(current_user_id)

        return WalletResponse(
            balance=user.balance,
            transactions=[
                TransactionPublic.model_validate(tx) for tx in transactions
            ],
        )

    async def deposit(
        self, current_user_id: UUID, data: DepositRequest
    ) -> WalletResponse:
        # Lock user row to prevent concurrent deposits
        user = await self.user_repository.get_for_update(current_user_id)
        if not user:
            raise AppException(
                code="USER_NOT_FOUND",
                message="User not found",
                status_code=404,
            )

        # Credit balance
        user.balance += data.amount
        await self.user_repository.update(user)

        # Record DEPOSIT transaction
        tx = Transaction(
            user_id=user.user_id,
            amount=data.amount,
            transaction_type=TransactionType.DEPOSIT,
        )
        await self.transaction_repository.create(tx)

        await self.session.commit()

        # Return updated wallet
        transactions = await self.transaction_repository.get_by_user_id(
            current_user_id
        )
        return WalletResponse(
            balance=user.balance,
            transactions=[
                TransactionPublic.model_validate(t) for t in transactions
            ],
        )
