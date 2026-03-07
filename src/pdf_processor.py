import io

import fitz  # PyMuPDF
from PIL import Image


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

    def extract_page_as_image(self, page_number: int, dpi: int = 300) -> Image.Image:
        """
        Extract a specific page from the PDF as a PIL Image.
        page_number is 1-indexed.
        """
        if not self.doc:
            raise RuntimeError("PDF document is not opened. Use 'with' statement.")

        if page_number < 1 or page_number > len(self.doc):
            raise ValueError(
                f"Invalid page number {page_number}. Must be between 1 and {len(self.doc)}."
            )

        page = self.doc[page_number - 1]  # 0-indexed in PyMuPDF

        # Calculate matrix for specified DPI (default is 72)
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        pix = page.get_pixmap(matrix=mat)

        # Convert to PIL Image
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        return image

    def extract_pages_as_images(
            self, start_page: int = 1, end_page: int = None, dpi: int = 300
    ):
        """
        Generator that yields (page_number, PIL.Image) for the specified range.
        """
        if not self.doc:
            raise RuntimeError("PDF document is not opened. Use 'with' statement.")

        if end_page is None:
            end_page = len(self.doc)

        for page_num in range(start_page, end_page + 1):
            yield page_num, self.extract_page_as_image(page_num, dpi=dpi)
