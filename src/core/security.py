import hashlib
import logging

import bcrypt

logger = logging.getLogger(__name__)


class PasswordHasher:
    """Класс для хэширования паролей.
    
    Использует двойное хеширование для обхода ограничения bcrypt в 72 байта:
    1. SHA256 (поддерживает любую длину) → фиксированный хеш
    2. Bcrypt (безопасное медленное хеширование) → финальный хеш
    """

    def _prehash_password(self, password: str) -> bytes:
        """Предварительное хеширование через SHA256 для поддержки паролей любой длины."""
        return hashlib.sha256(password.encode('utf-8')).digest()

    def verify_password(self, plain_pass: str, hashed_pass: str) -> bool:
        """Проверяет, соответствует ли пароль хэшу."""
        prehashed = self._prehash_password(plain_pass)
        return bcrypt.checkpw(prehashed, hashed_pass.encode('utf-8'))

    def get_password_hash(self, password: str) -> str:
        """Хэширует пароль. Поддерживает пароли любой длины."""
        logger.debug({
            "action": "PasswordHasher.get_password_hash",
            "stage": "start",
            "data": {"password_length": len(password)}
        })
        
        # Предварительное хеширование для обхода ограничения bcrypt
        prehashed = self._prehash_password(password)
        
        # Основное хеширование через bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(prehashed, salt)
        
        return hashed.decode('utf-8')


# Default password hasher instance
password_hasher = PasswordHasher()