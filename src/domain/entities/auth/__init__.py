"""Domain entities for authentication."""

from .blacklisted_token import BlacklistedToken
from .refresh_token import RefreshToken

__all__ = ["BlacklistedToken", "RefreshToken"]
