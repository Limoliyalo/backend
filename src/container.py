from dependency_injector import containers, providers

from src.adapters.database.session import session_manager
from src.adapters.repositories.picture_repository.sqlalchemy import (
    SQLAlchemyPicturesRepository,
)
from src.adapters.repositories.user_pictures_repository.sqlalchemy import (
    SQLAlchemyUserPicturesRepository,
)
from src.adapters.repositories.user_repository.sqlalchemy import (
    SQLAlchemyUsersRepository,
)
from src.core.settings import settings
from src.use_cases.pictures.get_picture import GetLatestPictureUseCase
from src.use_cases.pictures.list_opened_pictures import ListOpenedPicturesUseCase
from src.use_cases.pictures.open_picture import OpenPictureUseCase
from src.use_cases.pictures.upsert_picture import UpsertPictureUseCase
from src.use_cases.users.get_user import GetUserUseCase
from src.use_cases.users.upsert_user import UpsertUserUseCase


class ApplicationContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["src.drivers.rest"])

    settings_provider = providers.Object(settings)

    session_factory = providers.Object(session_manager.async_session)

    users_repository = providers.Factory(
        SQLAlchemyUsersRepository, session_factory=session_factory
    )
    pictures_repository = providers.Factory(
        SQLAlchemyPicturesRepository, session_factory=session_factory
    )
    user_pictures_repository = providers.Factory(
        SQLAlchemyUserPicturesRepository, session_factory=session_factory
    )

    get_user_use_case = providers.Factory(
        GetUserUseCase, users_repository=users_repository
    )
    upsert_user_use_case = providers.Factory(
        UpsertUserUseCase, users_repository=users_repository
    )

    upsert_picture_use_case = providers.Factory(
        UpsertPictureUseCase, pictures_repository=pictures_repository
    )
    get_picture_use_case = providers.Factory(
        GetLatestPictureUseCase, pictures_repository=pictures_repository
    )
    open_picture_use_case = providers.Factory(
        OpenPictureUseCase,
        users_repository=users_repository,
        pictures_repository=pictures_repository,
        user_pictures_repository=user_pictures_repository,
    )
    list_opened_pictures_use_case = providers.Factory(
        ListOpenedPicturesUseCase,
        users_repository=users_repository,
        user_pictures_repository=user_pictures_repository,
    )
