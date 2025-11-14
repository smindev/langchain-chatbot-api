from typing import Iterable, List
import os

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
FAISS_DIR = os.getenv("FAISS_DIR", "storage/faiss")

_embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)
_text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
_store = None


def get_store():
    global _store
    if _store is not None:
        return _store
    try:
        _store = FAISS.load_local(FAISS_DIR, _embeddings, allow_dangerous_deserialization=True)
    except Exception:
        _store = None
    return _store


def ingest_texts(texts: Iterable[str]) -> int:
    docs: List[Document] = [Document(page_content=t) for t in texts if t.strip()]
    if not docs:
        return 0
    splits = _text_splitter.split_documents(docs)

    global _store
    store = get_store()
    if store is None:
        _store = FAISS.from_documents(splits, _embeddings)
    else:
        store.add_documents(splits)
    try:
        _store.save_local(FAISS_DIR)
    except Exception:
        pass
    return len(splits)


def similarity_search(query: str, k: int = 4) -> List[Document]:
    store = get_store()
    if store is None:
        return []
    return store.similarity_search(query, k=k)
