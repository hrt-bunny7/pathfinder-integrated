"""
Document Extractor Module for Career Guidance Resume Analysis.
Supports text extraction from:
1. PDF documents (digital and scanned) via PyMuPDF (fitz)
2. Resume Images (PNG, JPG, JPEG, WEBP, TIFF, BMP) via Pillow (PIL) and Tesseract OCR (pytesseract)
3. Robust text cleaning to remove OCR noise and formatting artifacts.
"""

import io
import os
import re
from typing import Union, BinaryIO, Optional
from pathlib import Path

# Supported image extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".tif", ".bmp"}


def clean_extracted_text(text: str) -> str:
    """
    Cleans raw text extracted from PDF or OCR images:
    - Fixes OCR artifacts (stray pipes, broken bullet points).
    - Unwraps hyphenated words split across lines (e.g. 'engi-\nneer' -> 'engineer').
    - Normalizes unicode quotation marks, dashes, bullets, and non-breaking spaces.
    - Strips excessive blank lines and leading/trailing whitespace.
    """
    if not text:
        return ""

    # Replace non-breaking spaces, form feeds, tabs
    text = text.replace("\xa0", " ").replace("\x0c", "\n").replace("\t", " ")

    # Normalize unicode bullets to standard markdown bullets
    text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\uf0b7▪►■]", "\n- ", text)

    # Normalize dashes and quotes
    text = re.sub(r"[\u2013\u2014]", "-", text)
    text = re.sub(r"[\u2018\u2019]", "'", text)
    text = re.sub(r"[\u201C\u201D]", '"', text)

    # Rejoin hyphenated line wraps (e.g. 'deve- \n loper' -> 'developer')
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

    # Clean stray OCR pipe characters often mistakenly read from resume layout borders
    text = re.sub(r"(?<=\n)\s*\|\s*", "", text)
    text = re.sub(r"\s*\|\s*(?=\n)", "", text)

    # Normalize multiple newlines and spaces line-by-line
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                cleaned_lines.append("")
                prev_blank = True
        else:
            cleaned_lines.append(line)
            prev_blank = False

    return "\n".join(cleaned_lines).strip()


def extract_text_from_pdf(source: Union[str, bytes, BinaryIO]) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz) or pypdf fallback.
    If the PDF contains scanned images without selectable text, attempts OCR.
    """
    has_fitz = False
    has_pypdf = False

    try:
        import fitz
        has_fitz = True
    except ImportError:
        pass

    try:
        import pypdf
        has_pypdf = True
    except ImportError:
        pass

    if not has_fitz and not has_pypdf:
        raise ImportError(
            "A PDF reader is required. Please install PyMuPDF or pypdf:\n"
            "    pip install pymupdf\n"
            "    pip install pypdf"
        )

    # Method 1: PyMuPDF (fitz)
    if has_fitz:
        doc = None
        try:
            if isinstance(source, str):
                if not os.path.exists(source):
                    raise FileNotFoundError(f"PDF file not found: {source}")
                doc = fitz.open(source)
            elif isinstance(source, bytes):
                doc = fitz.open(stream=source, filetype="pdf")
            elif hasattr(source, "read"):
                data = source.read()
                doc = fitz.open(stream=data, filetype="pdf")
            else:
                raise ValueError("Unsupported source format for PDF.")

            full_text = []
            has_text = False
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                if text and text.strip():
                    full_text.append(text)
                    has_text = True

            combined_text = "\n".join(full_text)

            # Scanned PDF fallback
            if not has_text or len(combined_text.strip()) < 50:
                ocr_text = _ocr_pdf_pages(doc)
                if ocr_text:
                    combined_text = ocr_text

            return clean_extracted_text(combined_text)
        finally:
            if doc is not None:
                doc.close()

    # Method 2: pypdf (pure Python fallback)
    if has_pypdf:
        if isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(f"PDF file not found: {source}")
            reader = pypdf.PdfReader(source)
        elif isinstance(source, bytes):
            reader = pypdf.PdfReader(io.BytesIO(source))
        elif hasattr(source, "read"):
            data = source.read()
            reader = pypdf.PdfReader(io.BytesIO(data))
        else:
            raise ValueError("Unsupported source format for PDF.")

        full_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t and t.strip():
                full_text.append(t)

        return clean_extracted_text("\n".join(full_text))


def _ocr_pdf_pages(doc) -> str:
    """Fallback OCR for scanned PDFs with image-only pages."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return ""

    ocr_pages = []
    for page in doc:
        # Render page to high-res image pixmap
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        page_text = pytesseract.image_to_string(img)
        if page_text:
            ocr_pages.append(page_text)

    return "\n".join(ocr_pages)


def extract_text_from_image(source: Union[str, bytes, BinaryIO]) -> str:
    """
    Extracts text from an image (PNG, JPG, JPEG, WEBP, etc.) using Tesseract OCR.
    
    Args:
        source: File path, image bytes, or file-like object.
    
    Returns:
        Cleaned extracted resume text.
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("Pillow is required for image processing. Install it with: pip install pillow")

    try:
        import pytesseract
    except ImportError:
        raise ImportError(
            "pytesseract is required for image OCR. Install it with: pip install pytesseract\n"
            "Also ensure Tesseract-OCR engine is installed on your OS (e.g., https://github.com/UB-Mannheim/tesseract/wiki)."
        )

    # Open the image
    if isinstance(source, str):
        if not os.path.exists(source):
            raise FileNotFoundError(f"Image file not found: {source}")
        img = Image.open(source)
    elif isinstance(source, bytes):
        img = Image.open(io.BytesIO(source))
    elif hasattr(source, "read"):
        img = Image.open(source)
    else:
        raise ValueError("Unsupported source format for image.")

    try:
        # Optional image enhancement can be done here (convert to grayscale)
        if img.mode != "RGB":
            img = img.convert("RGB")
        raw_text = pytesseract.image_to_string(img)
        return clean_extracted_text(raw_text)
    finally:
        img.close()


def extract_resume_text(source: Union[str, bytes, BinaryIO], file_type: Optional[str] = None) -> str:
    """
    Unified entry point: automatically detects whether the input is a PDF or an Image,
    and extracts cleaned text.
    
    Args:
        source: File path, file bytes, or file-like object.
        file_type: Optional explicit file type/extension (e.g. 'pdf', 'png', 'jpg').
    
    Returns:
        Cleaned text string ready for profile analysis.
    """
    ext = ""
    if file_type:
        ext = f".{file_type.lower().lstrip('.')}"
    elif isinstance(source, str):
        ext = Path(source).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(source)
    elif ext in IMAGE_EXTENSIONS:
        return extract_text_from_image(source)
    elif isinstance(source, str) and os.path.exists(source):
        # Infer extension from path
        if source.lower().endswith(".pdf"):
            return extract_text_from_pdf(source)
        else:
            return extract_text_from_image(source)
    else:
        # Default try PDF first, fallback to image
        try:
            return extract_text_from_pdf(source)
        except Exception:
            return extract_text_from_image(source)
