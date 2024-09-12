from pydantic import (
    BaseModel,
    Field,
)
from typing import List, Optional


class VersionModel(BaseModel):
    """Версия API"""
    version: str = Field(default=None, title='Версия', description='Номер версии в виде X.Y[.Z]')


class Query(BaseModel):
    queries: List[str]
    n_results: int = 3


class GoogleSheetInfo(BaseModel):
    sheet_id: str
    gid: str
    collection: Optional[str] = None


class BatchAddition(BaseModel):
    documents: List[str]
    metadata: List[dict]
    collection: Optional[str] = None
