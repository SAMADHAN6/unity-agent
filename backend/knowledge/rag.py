"""
RAG Pipeline — loads Unity docs into a vector store and retrieves relevant chunks.
Uses chromadb 1.x + HuggingFace local embeddings (no API key needed).
"""

import os
from typing import List

import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings          # local embeddings, free
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader

COLLECTION_NAME = "unity_docs"
VECTOR_DB_PATH  = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/vectordb")
)
DOCS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/docs")
)

# Small, fast model — downloads once (~90 MB), runs locally forever
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_vectorstore: Chroma | None = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def _get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=VECTOR_DB_PATH)


def build_knowledge_base() -> None:
    """
    Load .txt files from data/docs/, chunk + embed them,
    and save to the local Chroma vector store.
    """
    global _vectorstore

    print("Loading Unity documents...")
    loader = DirectoryLoader(DOCS_PATH, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()

    if not documents:
        print("No documents found in data/docs/. Add .txt files to build the knowledge base.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks from {len(documents)} documents.")

    print("Loading embedding model (downloads on first run)...")
    embeddings = _get_embeddings()
    client = _get_chroma_client()

    # Delete existing collection so rebuilds don't duplicate
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    _vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=client,
        collection_name=COLLECTION_NAME,
    )
    print("Knowledge base built and saved.")


def load_knowledge_base() -> None:
    """Load an existing vector store from disk (if it exists)."""
    global _vectorstore

    if not os.path.exists(VECTOR_DB_PATH):
        print("No knowledge base found. Call /build-kb or run build_knowledge_base() first.")
        return

    try:
        embeddings = _get_embeddings()
        client = _get_chroma_client()
        _vectorstore = Chroma(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
        )
        print("Knowledge base loaded.")
    except Exception as e:
        print(f"Could not load knowledge base: {e}")


def search_unity_docs(query: str, top_k: int = 4) -> List[str]:
    """
    Search the vector store for the most relevant Unity doc chunks.
    Returns a list of text snippets.
    """
    if _vectorstore is None:
        load_knowledge_base()

    if _vectorstore is None:
        return []

    results = _vectorstore.similarity_search(query, k=top_k)
    return [doc.page_content for doc in results]
