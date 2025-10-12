import logging
import uuid
from dataclasses import dataclass

from src.core.security import PasswordHasher
from src.domain.entities.healthity.transactions import Transaction
from src.domain.entities.healthity.users import User
from src.domain.exceptions import UserNotFoundException
from src.domain.value_objects.telegram_id import TelegramId
from src.ports.repositories.healthity.transactions import TransactionsRepository
from src.ports.repositories.users import UsersRepository


@dataclass
class CreateUserInput:
    telegram_id: int
    password: str | None = None
    is_active: bool = True
    balance: int = 0


@dataclass
class UpdateUserInput:
    telegram_id: int
    password: str | None = None
    is_active: bool | None = None
    balance: int | None = None


class GetUserUseCase:
    def __init__(self, users_repository: UsersRepository) -> None:
        self._users_repository = users_repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute(self, telegram_id: int) -> User:
        self.logger.info(
            {
                "action": "GetUserUseCase.execute",
                "stage": "start",
                "data": {"telegram_id": telegram_id},
            }
        )

        user = await self._users_repository.get_by_telegram_id(TelegramId(telegram_id))

        if user is None:
            self.logger.warning(
                {
                    "action": "GetUserUseCase.execute",
                    "stage": "not_found",
                    "data": {"telegram_id": telegram_id},
                }
            )
            raise UserNotFoundException(telegram_id)

        self.logger.info(
            {
                "action": "GetUserUseCase.execute",
                "stage": "end",
                "data": {
                    "telegram_id": telegram_id,
                    "is_active": user.is_active,
                    "balance": user.balance,
                },
            }
        )
        return user


class CreateUserUseCase:
    def __init__(
        self, users_repository: UsersRepository, password_hasher: PasswordHasher
    ) -> None:
        self._users_repository = users_repository
        self._password_hasher = password_hasher
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute(self, data: CreateUserInput) -> User:
        self.logger.info(
            {
                "action": "CreateUserUseCase.execute",
                "stage": "start",
                "data": {
                    "telegram_id": data.telegram_id,
                    "is_active": data.is_active,
                    "balance": data.balance,
                    "has_password": data.password is not None,
                },
            }
        )

        telegram_id = TelegramId(data.telegram_id)

        self.logger.debug(
            {
                "action": "CreateUserUseCase.execute",
                "stage": "checking_existing",
                "data": {"telegram_id": data.telegram_id},
            }
        )
        existing = await self._users_repository.get_by_telegram_id(telegram_id)

        if existing:
            self.logger.error(
                {
                    "action": "CreateUserUseCase.execute",
                    "stage": "already_exists",
                    "data": {"telegram_id": data.telegram_id},
                }
            )
            raise ValueError(f"User with telegram_id {data.telegram_id} already exists")

        # Hash password if provided
        password_hash = (
            self._password_hasher.get_password_hash(data.password)
            if data.password
            else None
        )

        self.logger.debug(
            {
                "action": "CreateUserUseCase.execute",
                "stage": "password_hashed",
                "data": {"has_password": password_hash is not None},
            }
        )

        user = User(
            telegram_id=telegram_id,
            password_hash=password_hash,
            is_active=data.is_active,
            balance=data.balance,
        )

        self.logger.debug(
            {
                "action": "CreateUserUseCase.execute",
                "stage": "saving_to_db",
                "data": {"telegram_id": data.telegram_id},
            }
        )
        created_user = await self._users_repository.create(user)

        self.logger.info(
            {
                "action": "CreateUserUseCase.execute",
                "stage": "end",
                "data": {
                    "telegram_id": data.telegram_id,
                    "is_active": created_user.is_active,
                    "balance": created_user.balance,
                },
            }
        )
        return created_user


class ListUsersUseCase:
    def __init__(self, users_repository: UsersRepository) -> None:
        self._users_repository = users_repository

    async def execute(self, limit: int = 100, offset: int = 0) -> list[User]:
        return await self._users_repository.list_all(limit=limit, offset=offset)


class UpdateUserUseCase:
    def __init__(
        self, users_repository: UsersRepository, password_hasher: PasswordHasher
    ) -> None:
        self._users_repository = users_repository
        self._password_hasher = password_hasher

    async def execute(self, data: UpdateUserInput) -> User:
        telegram_id = TelegramId(data.telegram_id)
        user = await self._users_repository.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundException(data.telegram_id)

        if data.password is not None:
            password_hash = self._password_hasher.get_password_hash(data.password)
            user.update_password(password_hash)
        if data.is_active is not None:
            if data.is_active:
                user.activate()
            else:
                user.deactivate()
        if data.balance is not None:
            if data.balance < 0:
                raise ValueError("Balance cannot be negative")
            user.balance = data.balance
            user.touch()

        return await self._users_repository.update(user)


class DeleteUserUseCase:
    def __init__(self, users_repository: UsersRepository) -> None:
        self._users_repository = users_repository

    async def execute(self, telegram_id: int) -> None:
        user = await self._users_repository.get_by_telegram_id(TelegramId(telegram_id))
        if user is None:
            raise UserNotFoundException(telegram_id)
        await self._users_repository.delete(TelegramId(telegram_id))


@dataclass
class DepositInput:
    telegram_id: int
    amount: int
    description: str | None = None


class DepositUseCase:
    def __init__(
        self,
        users_repository: UsersRepository,
        transactions_repository: TransactionsRepository,
    ) -> None:
        self._users_repository = users_repository
        self._transactions_repository = transactions_repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute(self, data: DepositInput) -> User:
        self.logger.info(
            {
                "action": "DepositUseCase.execute",
                "stage": "start",
                "data": {"telegram_id": data.telegram_id, "amount": data.amount},
            }
        )

        telegram_id = TelegramId(data.telegram_id)
        user = await self._users_repository.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundException(data.telegram_id)

        # Пополнить баланс
        user.deposit(data.amount)
        updated_user = await self._users_repository.update(user)

        # Создать транзакцию
        transaction = Transaction(
            id=uuid.uuid4(),
            user_tg_id=telegram_id,
            amount=data.amount,
            balance_after=updated_user.balance,
            type="deposit",
            description=data.description or "Пополнение баланса",
        )
        await self._transactions_repository.add(transaction)

        self.logger.info(
            {
                "action": "DepositUseCase.execute",
                "stage": "end",
                "data": {
                    "telegram_id": data.telegram_id,
                    "amount": data.amount,
                    "new_balance": updated_user.balance,
                },
            }
        )
        return updated_user


@dataclass
class WithdrawInput:
    telegram_id: int
    amount: int
    description: str | None = None


class WithdrawUseCase:
    def __init__(
        self,
        users_repository: UsersRepository,
        transactions_repository: TransactionsRepository,
    ) -> None:
        self._users_repository = users_repository
        self._transactions_repository = transactions_repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute(self, data: WithdrawInput) -> User:
        self.logger.info(
            {
                "action": "WithdrawUseCase.execute",
                "stage": "start",
                "data": {"telegram_id": data.telegram_id, "amount": data.amount},
            }
        )

        telegram_id = TelegramId(data.telegram_id)
        user = await self._users_repository.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundException(data.telegram_id)

        # Списать средства
        user.withdraw(data.amount)
        updated_user = await self._users_repository.update(user)

        # Создать транзакцию
        transaction = Transaction(
            id=uuid.uuid4(),
            user_tg_id=telegram_id,
            amount=-data.amount,
            balance_after=updated_user.balance,
            type="withdrawal",
            description=data.description or "Списание средств",
        )
        await self._transactions_repository.add(transaction)

        self.logger.info(
            {
                "action": "WithdrawUseCase.execute",
                "stage": "end",
                "data": {
                    "telegram_id": data.telegram_id,
                    "amount": data.amount,
                    "new_balance": updated_user.balance,
                },
            }
        )
        return updated_user


@dataclass
class ChangePasswordInput:
    telegram_id: int
    old_password: str
    new_password: str


class ChangePasswordUseCase:
    def __init__(
        self,
        users_repository: UsersRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._users_repository = users_repository
        self._password_hasher = password_hasher
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute(self, data: ChangePasswordInput) -> User:
        self.logger.info(
            {
                "action": "ChangePasswordUseCase.execute",
                "stage": "start",
                "data": {"telegram_id": data.telegram_id},
            }
        )

        telegram_id = TelegramId(data.telegram_id)
        user = await self._users_repository.get_by_telegram_id(telegram_id)

        if user is None:
            raise UserNotFoundException(data.telegram_id)

        # Проверить старый пароль
        if user.password_hash is None:
            raise ValueError("User does not have a password set")

        if not self._password_hasher.verify_password(
            data.old_password, user.password_hash
        ):
            raise ValueError("Old password is incorrect")

        # Установить новый пароль
        new_password_hash = self._password_hasher.get_password_hash(data.new_password)
        user.update_password(new_password_hash)
        updated_user = await self._users_repository.update(user)

        self.logger.info(
            {
                "action": "ChangePasswordUseCase.execute",
                "stage": "end",
                "data": {"telegram_id": data.telegram_id},
            }
        )
        return updated_user
