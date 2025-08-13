from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    system_prompt: Optional[str] = None
    max_new_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None

class ChatResponseChunk(BaseModel):
    token: str
    finish_reason: str | None = None