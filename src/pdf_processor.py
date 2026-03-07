from typing import Optional

import fitz  # PyMuPDF


class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None

    def __enter__(self):
        self.doc = fitz.open(self.pdf_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.doc:
            self.doc.close()

    def get_page_count(self) -> int:
        if not self.doc:
            raise RuntimeError("PDF document is not opened. Use 'with' statement.")
        return len(self.doc)

    def extract_page_as_pdf(self, page_number: int) -> bytes:
        """
        Extract a specific page from the PDF as PDF bytes.
        page_number is 1-indexed.
        """
        if not self.doc:
            raise RuntimeError("PDF document is not opened. Use 'with' statement.")

        if page_number < 1 or page_number > len(self.doc):
            raise ValueError(
                f"Invalid page number {page_number}. Must be between 1 and {len(self.doc)}."
            )

        new_doc = fitz.open()
        new_doc.insert_pdf(self.doc, from_page=page_number - 1, to_page=page_number - 1)
        pdf_bytes = new_doc.write()
        new_doc.close()
        return pdf_bytes

    def extract_pages_as_pdfs(
            self, start_page: int = 1, end_page: Optional[int] = None
    ):
        """
        Generator that yields (page_number, pdf_bytes) for the specified range.
        """
        if not self.doc:
            raise RuntimeError("PDF document is not opened. Use 'with' statement.")

        if end_page is None:
            end_page = len(self.doc)

        for page_num in range(start_page, end_page + 1):
            yield page_num, self.extract_page_as_pdf(page_num)
