from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from services import vectorstore

router = APIRouter()

class IngestRequest(BaseModel):
    texts: List[str]

class IngestResponse(BaseModel):
    chunks_added: int

@router.post("/ingest", response_model=IngestResponse)
async def ingest(req: IngestRequest):
    try:
        n = vectorstore.ingest_texts(req.texts)
        return IngestResponse(chunks_added=n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
