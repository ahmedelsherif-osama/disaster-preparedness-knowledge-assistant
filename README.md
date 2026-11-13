# Disaster Preparedness Knowledge Assistant

A small Retrieval-Augmented Generation (RAG) prototype that answers disaster preparedness questions using information retrieved from uploaded reference documents.

**Note:** This is an experimental knowledge assistant, not an emergency response system. Its answers should not replace official guidance or professional advice.

## Features

- Upload PDF documents to build a disaster preparedness knowledge base.
- Validate uploaded PDFs for file type, size, page count, and extractable text.
- Prevent duplicate uploads using SHA-256 file hashes.
- Extract and split document text into overlapping chunks.
- Generate embeddings using Google's Gemini embedding model.
- Store document chunks in a persistent Chroma vector database.
- Retrieve relevant content and generate context-grounded answers using Groq.
- Maintain chat history during the Streamlit session.

## How It Works

1. A user uploads a PDF document.
2. The application validates the file.
3. Text is extracted and split into chunks.
4. Google Gemini generates embeddings for the chunks.
5. Chunks and embeddings are stored in Chroma.
6. When a user asks a question, Chroma retrieves relevant chunks.
7. The retrieved context is passed to the Groq language model.
8. The model generates an answer based on the provided context.

## Technology Stack

- **Python** — application logic
- **Streamlit** — user interface
- **LangChain** — document processing and model integration
- **Google Gemini Embeddings** — text embeddings
- **Chroma** — vector storage and similarity search
- **Groq** — language model inference
- **PyPDF** — PDF validation and text extraction
- **Pytest** — automated tests
- **Ruff** — linting and formatting

## Getting Started

### Prerequisites

- Python 3.10 or later
- A Groq API key
- A Google AI API key

### Installation

Clone the repository:

```bash
git clone https://github.com/ahmedelsherif-osama/disaster-preparedness-knowledge-assistant.git
cd disaster-preparedness-knowledge-assistant
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
```

Keep API keys private. Do not commit your `.env` file.

### Run the Application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal.

## Using the Application

1. Upload a PDF using the file uploader.
2. Wait for the document to be processed and indexed.
3. Enter a disaster preparedness question in the chat input.
4. The assistant retrieves relevant document content and generates an answer.

### PDF Upload Limits

- PDF files only.
- Maximum file size: 10 MB.
- Maximum page count: 100 pages.
- PDFs must contain extractable text.
- Maximum of 10 unique PDFs in the knowledge base.

## Running Tests

Run the automated tests:

```bash
python -m pytest -v
```

Run Ruff checks:

```bash
ruff check .
```

Format the code:

```bash
ruff format .
```

## Project Structure

```text
project/
├── app.py                  # Streamlit interface and chat workflow
├── config.py               # Application configuration
├── vector_store.py         # Chroma vector database initialization
├── document_processor.py   # PDF validation, processing, and indexing
├── tests/                  # Automated tests
├── chroma_db/              # Persistent vector database (created at runtime)
├── .env                    # API keys (not committed)
└── requirements.txt        # Python dependencies
```

## Data and Persistence

The Chroma database is stored locally in `chroma_db/`. The application also creates a `processed_files.json` registry to track previously indexed documents.

These runtime files, uploaded PDFs, and API credentials should not be committed to version control.

## Limitations

- Answers depend on the quality and coverage of the uploaded documents.
- The assistant may produce incomplete or inaccurate answers.
- Scanned PDFs without extractable text are not supported.
- Google and Groq API access, quotas, and network availability affect operation.
- This prototype has not been designed or validated for operational emergency use.