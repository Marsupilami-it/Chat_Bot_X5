from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MLServiceConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env'
    )

    ml_service_host: str = Field(validation_alias='ML_HOST', default="ml-service")

    ml_service_port: int = Field(validation_alias='ML_PORT', default="8000")

    ml_service_protocol: str = Field(validation_alias='ML_PROTOCOL', default="http")


ml_config = MLServiceConfig()


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env'
    )

    redis_host: str = Field(validation_alias='REDIS_HOST', default="redis")
    redis_port: int = Field(validation_alias='REDIS_PORT', default="6379")
    redis_db: int = Field(validation_alias='REDIS_DB', default="0")
    redis_password: str = Field(validation_alias='REDIS_PASSWORD', default="")

    redis_user: str = Field(validation_alias='REDIS_USER', default="redis")
    redis_user_password: str = Field(validation_alias='REDIS_USER_PASSWORD', default="redis")


redis_config = RedisConfig()
