import os
from typing import Generator, List

try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None

try:
    from langchain_community.chat_models import ChatOllama
except Exception:
    ChatOllama = None

from . import vectorstore


_llm = None


def _get_llm():
    global _llm
    if _llm is not None:
        return _llm
    openai_key = os.getenv("OPENAI_API_KEY")
    provider = os.getenv("LLM_PROVIDER", "openai" if openai_key else "ollama").lower()
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))

    if provider == "openai" and ChatOpenAI is not None and openai_key:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        _llm = ChatOpenAI(model=model, temperature=temperature)
        return _llm

    if provider == "ollama" and ChatOllama is not None:
        model = os.getenv("OLLAMA_MODEL", "llama3.1")
        _llm = ChatOllama(model=model, temperature=temperature)
        return _llm

    raise RuntimeError(
        "No LLM provider available. Set OPENAI_API_KEY or install Ollama."
    )


def _build_context(question: str, k: int = 4) -> str:
    docs = vectorstore.similarity_search(question, k=k)
    ctx = []
    for i, d in enumerate(docs, start=1):
        prefix = f"[Chunk {i}]"
        ctx.append(f"{prefix}\n{d.page_content}")
    return "\n\n".join(ctx) if ctx else ""


def _prompt(question: str, context: str) -> str:
    sys = (
        "You are a helpful assistant. Use ONLY the provided context to answer. "
        "If the answer isn't in the context, say you don't know. Be concise."
    )
    return f"{sys}\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"


def _last_user(messages: List[dict]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return m.get("content", "")
    return messages[-1]["content"] if messages else ""


def answer(messages: List[dict]) -> str:
    llm = _get_llm()
    question = _last_user(messages)
    context = _build_context(question)
    prompt = _prompt(question, context)
    try:
        resp = llm.invoke(prompt)
        return getattr(resp, "content", str(resp))
    except Exception:
        out = []
        for chunk in stream_answer(messages):
            out.append(chunk)
        return "".join(out)


def stream_answer(messages: List[dict]) -> Generator[str, None, None]:
    llm = _get_llm()
    question = _last_user(messages)
    context = _build_context(question)
    prompt = _prompt(question, context)

    try:
        for chunk in llm.stream(prompt):  # type: ignore
            token = getattr(chunk, "content", None)
            yield token if token is not None else str(chunk)
    except Exception:
        yield answer(messages)
