"""OCR Engine — Tesseract OCR for scanned PDFs."""
import os
import tempfile
import io
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Set tessdata path
os.environ["TESSDATA_PREFIX"] = r"C:/Users/Lenovo/Documents/Codex/2026-06-29/vps-firefox-hysteria-4000-2-8/tessdata"

LANG_MAP = {".en.": "eng", ".zh.": "chi_sim", ".ar.": "ara"}
DEFAULT_LANG = "eng+chi_sim"

def detect_language(filename):
    for key, lang in LANG_MAP.items():
        if key in filename.lower():
            return lang
    return DEFAULT_LANG

def preprocess_image(img):
    img = img.convert("L")
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    img = img.filter(ImageFilter.SHARPEN)
    return img

def ocr_image(img, lang=DEFAULT_LANG, preprocess=True):
    if preprocess:
        img = preprocess_image(img)
    return pytesseract.image_to_string(img, lang=lang, config="--oem 3 --psm 6")

def ocr_page(doc, page_num, lang=DEFAULT_LANG, dpi=300):
    from . import pdf_loader
    img_bytes = pdf_loader.page_to_image(doc, page_num, dpi)
    img = Image.open(io.BytesIO(img_bytes))
    return ocr_image(img, lang)
