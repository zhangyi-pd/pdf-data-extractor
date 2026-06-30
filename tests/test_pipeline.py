import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.pipeline import process_pdf

OUT = r"C:/Users/Lenovo/Documents/Codex/2026-06-29/vps-firefox-hysteria-4000-2-8/pdf-data-extractor/output"

pdf1 = r"D:/codexproject/multilingual-doc-generator/output/pdfs/en_invoice_001.pdf"
print("=" * 60)
print("TEST 1: Digital English Invoice")
print("=" * 60)
r1 = process_pdf(pdf1, output_dir=OUT)
print("Pages: %s, Method: %s, Time: %ss" % (r1["page_count"], r1["method"], r1["processing_time_seconds"]))
print("Type: %s" % r1["extracted"].get("document_type"))

pdf2 = r"D:/codexproject/multilingual-doc-generator/output/pdfs/zh_contract_001.pdf"
print()
print("=" * 60)
print("TEST 2: Chinese Contract (force OCR)")
print("=" * 60)
r2 = process_pdf(pdf2, output_dir=OUT, lang="chi_sim", force_ocr=True)
print("Pages: %s, Method: %s, Time: %ss" % (r2["page_count"], r2["method"], r2["processing_time_seconds"]))
preview = r2["extracted"].get("_text_preview", "")[:300]
print("Preview: %s" % preview)

print()
print("ALL TESTS COMPLETE")
