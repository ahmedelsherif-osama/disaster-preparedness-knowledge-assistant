"""Central configuration for application limits, storage, models, and API credentials."""

import os

from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()

# Maximum allowed PDF upload size (10 MB).
MAX_FILE_SIZE = 10 * 1024 * 1024

# Maximum number of pages allowed per PDF.
MAX_PAGES = 100

# Maximum number of unique PDFs allowed in the knowledge base.
MAX_DOCUMENTS = 10

# Chroma vector database settings.
CHROMA_COLLECTION_NAME = "disaster_knowledge"
CHROMA_PERSIST_DIRECTORY = "./chroma_db"

# AI model configuration.
EMBEDDING_MODEL = "gemini-embedding-2-preview"
LLM_MODEL = "openai/gpt-oss-20b"

# Groq API key, loaded from the environment.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
