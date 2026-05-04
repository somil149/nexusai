"""RAG pipeline - document ingestion, chunking, vector search."""
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import settings
from pathlib import Path
import os

_embeddings = None
_vectorstore = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            persist_directory=settings.chroma_dir,
            embedding_function=get_embeddings(),
        )
    return _vectorstore

async def ingest_document(file_path: str, session_id: str = "") -> int:
    """Load, chunk and embed a document. Returns chunk count."""
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        loader = PyPDFLoader(str(path))
    else:
        loader = TextLoader(str(path), encoding="utf-8")

    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    for chunk in chunks:
        chunk.metadata["session_id"] = session_id
        chunk.metadata["source"] = path.name

    vs = get_vectorstore()
    vs.add_documents(chunks)
    return len(chunks)

async def search_documents(query: str, session_id: str = "", k: int = 5) -> list[dict]:
    """Semantic search over ingested documents."""
    vs = get_vectorstore()
    filter_dict = {"session_id": session_id} if session_id else None
    results = vs.similarity_search_with_score(query, k=k, filter=filter_dict)
    return [
        {"content": doc.page_content, "source": doc.metadata.get("source", ""), "score": float(score)}
        for doc, score in results
    ]

def build_rag_context(results: list[dict]) -> str:
    if not results:
        return ""
    context = "\n\n".join(f"[{r['source']}]\n{r['content']}" for r in results)
    return f"<context>\n{context}\n</context>\n\n"
