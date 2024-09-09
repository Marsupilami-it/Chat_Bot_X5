from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

"""тут будут конфиги подключений к БД и тому подобное, лучше делать через pydantic_settings
внизу оставил пример, которым кейклоак подключал"""
class BaseAuthConfig(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=('.env', '.env.prod')
    )

    server_url: str = Field(validation_alias='server_url', default="http://localhost:8080")

    realm: str = Field(validation_alias='realm', default="master")

    client_id: str = Field(validation_alias='client_id', default="user")

    client_secret: str = Field(validation_alias='client_secret', default="")

    authorization_url: str = Field(
        validation_alias='authorization_url',
        default="http://localhost:8080/auth/realms/master/protocol/openid-connect/auth"
    )

    token_url: str = Field(
        validation_alias='token_url',
        default="http://localhost:8080/auth/realms/master/protocol/openid-connect/token")


connection_settings = BaseAuthConfig()