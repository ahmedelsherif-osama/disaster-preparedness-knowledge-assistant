"""PDF validation, processing, chunking, and indexing for the knowledge base."""

import hashlib
import json
import os
from io import BytesIO

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY,
    EMBEDDING_MODEL,
    MAX_FILE_SIZE,
    MAX_PAGES,
)


def get_file_hash(file_bytes):
    """Generate a SHA-256 hash to identify uploaded files."""
    return hashlib.sha256(file_bytes).hexdigest()


def load_processed_hashes():
    """Load hashes of previously processed PDFs from the registry file.

    Returns an empty list if the registry does not exist.
    Raises RuntimeError if the registry cannot be read or is invalid.
    """
    if not os.path.exists("processed_files.json"):
        return []

    try:
        with open("processed_files.json", "r") as f:
            hashes = json.load(f)

        if not isinstance(hashes, list):
            raise TypeError("Invalid registry format.")

        return hashes

    except (json.JSONDecodeError, OSError, ValueError) as e:
        raise RuntimeError("Could not read the processed-files registry.") from e


def validate_pdf(file_bytes, filename):
    """Validate an uploaded PDF's format, size, page count, and text content.

    Returns:
        A tuple containing (is_valid, error_message).
        The error message is None when validation succeeds.
    """
    if not filename.lower().endswith(".pdf"):
        return False, "Only PDF files are supported."

    if not file_bytes:
        return False, "The uploaded file is empty."

    if len(file_bytes) > MAX_FILE_SIZE:
        return False, "PDF exceeds the 10 MB size limit."

    try:
        reader = PdfReader(BytesIO(file_bytes))

        if not reader.pages:
            return False, "The PDF contains no pages."

        if len(reader.pages) > MAX_PAGES:
            return False, "PDF exceeds the 100-page limit."

        if not any(page.extract_text() for page in reader.pages):
            return False, "No extractable text found in this PDF."

    except (PdfReadError, OSError, ValueError):
        return False, "The PDF is invalid, corrupted, or unreadable."

    return True, None


def document_process(path):
    """Extract, split, embed, and index a PDF in the persistent Chroma database.

    Args:
        path: Path to the PDF file.

    Returns:
        The initialized Chroma vector database.

    Raises:
        RuntimeError: If document processing or indexing fails.
    """
    try:
        loader = PyPDFLoader(path)
        docs = loader.load()

        for doc in docs:
            doc.metadata["source"] = os.path.basename(path)

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents(docs)

        if not docs:
            raise ValueError("No document content could be extracted.")

        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

        vector_db = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            embedding_function=embeddings,
        )

        vector_db.add_documents(docs)

        return vector_db

    except Exception as e:
        raise RuntimeError(f"Document processing failed: {e}") from e
