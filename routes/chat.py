import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Iterator

from schemas.chat import ChatRequest
from services import rag

router = APIRouter()

@router.post("/chat")
async def chat(req: ChatRequest):
    try:
        if req.stream:
            def generate() -> Iterator[bytes]:
                for token in rag.stream_answer([m.dict() for m in req.messages]):
                    data = {"content": token, "done": False}
                    yield f"data: {json.dumps(data)}\n\n".encode("utf-8")
                yield b"data: {\"content\": \"\", \"done\": true}\n\n"
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            answer = rag.answer([m.dict() for m in req.messages])
            return JSONResponse(content={"content": answer})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
