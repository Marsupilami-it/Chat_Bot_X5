from pydantic import (
    BaseModel
)
from typing import (List, Optional)


class Query(BaseModel):
    queries: List[str]
    n_results: int = 3


class GoogleSheetInfo(BaseModel):
    sheet_id: str
    gid: str
    collection: Optional[str] = None


class BatchAddition(BaseModel):
    documents: List[str]
    metadatas: List[dict]
    collection: Optional[str] = None
