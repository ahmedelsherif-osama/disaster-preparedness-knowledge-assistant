"""Streamlit interface for the Disaster Preparedness Knowledge Assistant.

Handles PDF uploads, document indexing, and retrieval-augmented chat.
"""

import json
import os

import streamlit as st
from langchain_groq import ChatGroq

from config import CHROMA_PERSIST_DIRECTORY, GROQ_API_KEY, LLM_MODEL, MAX_DOCUMENTS
from document_processor import (
    document_process,
    get_file_hash,
    load_processed_hashes,
    validate_pdf,
)
from vector_store import load_vector_db

# Initialize the language model and verify API configuration.
if not GROQ_API_KEY:
    st.error("Groq API key is missing. Check your .env file.")
    st.stop()

llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY)


# Initialize session state and load the existing vector database.
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

    if os.path.exists(CHROMA_PERSIST_DIRECTORY):
        try:
            st.session_state.vector_db = load_vector_db()
        except Exception as e:  # noqa: BLE001
            st.error("Could not load the knowledge base.")
            print(f"Chroma initialization error: {e}")


# Display the application title and description.
st.subheader("Disaster Preparedness Knowledge Assistant (ChatBot)")
st.markdown("#### `Ask anything`")


# Accept PDF uploads, validate them, and prevent duplicate indexing.
file = st.file_uploader(label="Select PDF file", key="pdf_uploader")

if file:
    file_bytes = file.getvalue()
    is_valid, error_message = validate_pdf(file_bytes, file.name)

    if not is_valid:
        st.error(error_message)

    else:
        file_hash = get_file_hash(file_bytes)
        processed_hashes = load_processed_hashes()

        if file_hash in processed_hashes:
            st.warning("This document is already in the knowledge base.")

        elif len(processed_hashes) >= MAX_DOCUMENTS:
            st.error("Knowledge base limit reached (10 PDFs).")

        else:
            with open("uploaded_document.pdf", "wb") as f:
                f.write(file_bytes)

            try:
                with st.spinner("Processing..."):
                    st.session_state.vector_db = document_process(
                        "uploaded_document.pdf"
                    )

                processed_hashes.append(file_hash)

                with open("processed_files.json", "w") as f:
                    json.dump(processed_hashes, f)

                st.success("Document processed successfully!")
                st.rerun()

            except Exception as e:  # noqa: BLE001
                st.error(f"Document processing failed: {e}")


# Display chat history and enable questions when the knowledge base is populated.
if (
    st.session_state.vector_db is not None
    and st.session_state.vector_db._collection.count() > 0
):
    for oneMessage in st.session_state.messages:
        st.chat_message(oneMessage["role"]).markdown(oneMessage["content"])

    query = st.chat_input("Ask anything...")

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user").markdown(query)

        # Retrieve relevant document chunks and generate a grounded answer.
        try:
            documents = st.session_state.vector_db.similarity_search(query)

            if not documents:
                answer = "I couldn't find relevant information in the knowledge base."

            else:
                context = "\n\n".join(doc.page_content for doc in documents)

                prompt = f"""
                You are a disaster preparedness knowledge assistant.
                Answer using only the provided context.
                
                Rules:
                - Ground answers: prioritize retrieved documents; don't invent facts.
                - Allow reasoning: draw reasonable conclusions from the context, but distinguish inference from explicit statements.
                - Correct tactfully: don't blindly accept false assumptions in a question; explain the correction.
                - Handle uncertainty: say when evidence is incomplete or conflicting, and ask for clarification when needed.
                - Avoid unnecessary abstention: answer the parts that are supported, even if the whole question can't be answered.
                - Preserve nuance: don't oversimplify complex or interdependent issues.

                Context:
                {context}

                Question:
                {query}
                """

                result = llm.invoke(prompt)
                answer = result.content

            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.chat_message("assistant").markdown(answer)

        except Exception as e:  # noqa: BLE001
            st.error("Unable to generate an answer. Please try again.")
            print(f"Chat error: {e}")
