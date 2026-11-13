from types import SimpleNamespace

import document_processor
from config import MAX_FILE_SIZE
from document_processor import (
    get_file_hash,
    validate_pdf,
)


def test_file_hash_is_consistent():
    file_bytes = b"sample pdf content"

    assert get_file_hash(file_bytes) == get_file_hash(file_bytes)


def test_duplicate_files_have_same_hash():
    file_one = b"same document"
    file_two = b"same document"

    assert get_file_hash(file_one) == get_file_hash(file_two)


def test_non_pdf_file_is_rejected():
    is_valid, error = validate_pdf(b"some content", "document.txt")

    assert is_valid is False
    assert error == "Only PDF files are supported."


def test_empty_pdf_is_rejected():
    valid, error = document_processor.validate_pdf(b"", "empty.pdf")

    assert valid is False
    assert error == "The uploaded file is empty."


def test_oversized_pdf_is_rejected():
    file_bytes = b"x" * (MAX_FILE_SIZE + 1)

    valid, error = document_processor.validate_pdf(file_bytes, "large.pdf")

    assert valid is False
    assert error == "PDF exceeds the 10 MB size limit."


def test_corrupted_pdf_is_rejected():
    valid, error = document_processor.validate_pdf(b"not a real PDF", "corrupted.pdf")

    assert valid is False
    assert error == "The PDF is invalid, corrupted, or unreadable."


def test_valid_pdf_is_accepted(monkeypatch):
    fake_page = SimpleNamespace(extract_text=lambda: "Disaster preparedness")
    fake_reader = SimpleNamespace(pages=[fake_page])

    monkeypatch.setattr(document_processor, "PdfReader", lambda _: fake_reader)

    valid, error = document_processor.validate_pdf(b"fake PDF", "valid.pdf")

    assert valid is True
    assert error is None
