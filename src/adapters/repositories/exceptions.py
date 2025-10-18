class RepositoryError(Exception):
    """Generic repository error."""


class IntegrityConstraintError(RepositoryError):
    """Database integrity constraint violation."""


class DuplicateEntityError(RepositoryError):
    """Entity already exists."""
