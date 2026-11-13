"""Initialize and load the persistent Chroma vector database."""

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY,
    EMBEDDING_MODEL,
)


def load_vector_db():
    """Load the Chroma collection using the configured embedding model."""
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    return Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        embedding_function=embeddings,
    )
