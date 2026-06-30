"""PDF Loader — load PDFs, extract text, convert pages to images."""
import os
import fitz


def load_pdf(filepath):
    """Load a PDF file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"PDF not found: {filepath}")
    return fitz.open(filepath)


def is_scanned(doc, threshold=0.1):
    """Detect if PDF is scanned (image-based, little extractable text)."""
    total = sum(len(page.get_text().strip()) for page in doc)
    avg = total / max(len(doc), 1)
    return avg < threshold * 100


def extract_text(doc):
    """Extract text from each page with block metadata."""
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        blocks = page.get_text("blocks")
        pages.append({
            "page": i + 1,
            "text": text.strip(),
            "char_count": len(text.strip()),
            "block_count": len(blocks),
            "blocks": [
                {
                    "type": "text" if b[6] == 0 else "image",
                    "x0": round(b[0], 1), "y0": round(b[1], 1),
                    "x1": round(b[2], 1), "y1": round(b[3], 1),
                    "text": b[4].strip() if len(b) > 4 and b[4] else ""
                }
                for b in blocks if len(b) >= 5
            ]
        })
    return pages


def page_to_image(doc, page_num, dpi=300):
    """Convert a PDF page to PNG image bytes for OCR."""
    page = doc[page_num]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    return pix.tobytes("png")
