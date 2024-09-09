from pydantic import (
    BaseModel,
    Field,
)

class VersionModel(BaseModel):
    """Версия API"""
    version: str = Field(default=None, title='Версия', description='Номер версии в виде X.Y[.Z]')

"""Модельки пидантик - валидация """

