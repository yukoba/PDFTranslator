import os

import fitz
import pytest

from src.pdf_processor import PDFProcessor


@pytest.fixture
def dummy_pdf_path():
    """Fixture to create and clean up a dummy PDF file for testing."""
    test_pdf_path = "test_dummy.pdf"
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((50, 50), "Test Page 1")
    page2 = doc.new_page()
    page2.insert_text((50, 50), "Test Page 2")
    doc.save(test_pdf_path)
    doc.close()

    yield test_pdf_path

    # Clean up after test
    if os.path.exists(test_pdf_path):
        os.remove(test_pdf_path)


def test_get_page_count(dummy_pdf_path):
    processor = PDFProcessor(dummy_pdf_path)
    with processor as proc:
        assert proc.get_page_count() == 2


def test_extract_page_as_image(dummy_pdf_path):
    processor = PDFProcessor(dummy_pdf_path)
    with processor as proc:
        img1 = proc.extract_page_as_image(1)
        assert img1 is not None
        assert img1.format == "PNG"


def test_extract_pages_as_images(dummy_pdf_path):
    processor = PDFProcessor(dummy_pdf_path)
    with processor as proc:
        pages = list(proc.extract_pages_as_images())
        assert len(pages) == 2
        assert pages[0][0] == 1
        assert pages[1][0] == 2


def test_processor_without_context_manager(dummy_pdf_path):
    processor = PDFProcessor(dummy_pdf_path)
    with pytest.raises(RuntimeError):
        processor.get_page_count()
