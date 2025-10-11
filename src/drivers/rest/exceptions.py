from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Базовое исключение для API"""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error: str = "Internal Server Error"

    def __init__(
        self, detail: str | None = None, headers: dict[str, str] | None = None
    ) -> None:
        self.detail = detail or self.error
        super().__init__(
            status_code=self.status_code, detail=self.detail, headers=headers
        )

    def __repr__(self) -> str:
        return f"Error: {self.error}, status: {self.status_code}, detail: {self.detail}"


class NotFoundException(BaseAPIException):
    """Ресурс не найден"""

    status_code = status.HTTP_404_NOT_FOUND
    error = "Not Found"


class BadRequestException(BaseAPIException):
    """Некорректный запрос"""

    status_code = status.HTTP_400_BAD_REQUEST
    error = "Bad Request"


class ConflictException(BaseAPIException):
    """Конфликт данных"""

    status_code = status.HTTP_409_CONFLICT
    error = "Conflict"


class UnauthorizedException(BaseAPIException):
    """Неавторизован"""

    status_code = status.HTTP_401_UNAUTHORIZED
    error = "Unauthorized"


class ForbiddenException(BaseAPIException):
    """Доступ запрещен"""

    status_code = status.HTTP_403_FORBIDDEN
    error = "Forbidden"


class ValidationException(BaseAPIException):
    """Ошибка валидации"""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error = "Validation Error"
