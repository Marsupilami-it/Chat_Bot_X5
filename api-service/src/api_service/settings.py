from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MLServiceConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env'
    )

    ml_service_host: str = Field(validation_alias='ML_HOST', default="ml-service")

    ml_service_port: int = Field(validation_alias='ML_PORT', default="8000")

    ml_service_protocol: str = Field(validation_alias='ML_PROTOCOL', default="http")


ml_settings = MLServiceConfig()
