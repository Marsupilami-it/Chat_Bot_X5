from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# class ChatRequest(BaseModel):
#     """Модель для хранения запросов пользователя"""
#     user_id: str
#     request_text: str
#     timestamp: datetime = Field(default_factory=datetime.utcnow)
#     response: Optional[str] = None
#     status: str = "pending"
#     error: Optional[str] = None
