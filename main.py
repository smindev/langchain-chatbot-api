from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router as chat_router
from routes.ingest import router as ingest_router

app = FastAPI(title="LangChain Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="")
app.include_router(ingest_router, prefix="")

@app.get("/health")
def health():
    return {"status": "ok"}
