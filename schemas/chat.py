from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str  # 'user' | 'assistant' | 'system'
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = True

class ChatResponseChunk(BaseModel):
    content: str
    done: bool = False

class ChatResponse(BaseModel):
    content: str
