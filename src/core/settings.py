from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: str
    echo: bool = False

    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseModel):
    host: str
    port: int
    password: str | None = None


class RabbitSettings(BaseModel):
    host: str
    port: int
    management_port: int
    user: str
    password: str

    @property
    def amqp_url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"


class JWTSettings(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int


class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    db_echo: bool = False

    redis_host: str
    redis_port: int
    redis_password: str | None

    rabbit_host: str
    rabbit_port: int
    rabbit_web_port: int
    rabbit_user: str
    rabbit_password: str
    rabbitmq_default_user: str | None = None
    rabbitmq_default_pass: str | None = None

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_minutes: int

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    @property
    def database(self) -> DatabaseSettings:
        return DatabaseSettings(
            host=self.db_host,
            port=self.db_port,
            name=self.db_name,
            user=self.db_user,
            password=self.db_password,
            echo=self.db_echo,
        )

    @property
    def redis(self) -> RedisSettings:
        return RedisSettings(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
        )

    @property
    def rabbitmq(self) -> RabbitSettings:
        return RabbitSettings(
            host=self.rabbit_host,
            port=self.rabbit_port,
            management_port=self.rabbit_web_port,
            user=self.rabbit_user,
            password=self.rabbit_password,
        )

    @property
    def jwt(self) -> JWTSettings:
        return JWTSettings(
            secret_key=self.jwt_secret_key,
            algorithm=self.jwt_algorithm,
            access_token_expire_minutes=self.jwt_access_token_expire_minutes,
            refresh_token_expire_minutes=self.jwt_refresh_token_expire_minutes,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]


settings = get_settings()
