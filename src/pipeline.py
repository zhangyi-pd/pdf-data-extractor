"""Pipeline — main orchestration: PDF in, structured data out."""
import os, json
from datetime import datetime
from . import pdf_loader, ocr_engine, extractor, exporter

def process_pdf(filepath, output_dir=None, lang=None, dpi=300, force_ocr=False):
    start = datetime.now()
    result = {
        "source": os.path.abspath(filepath),
        "filename": os.path.basename(filepath),
        "processed_at": start.isoformat(),
        "pages": [],
        "_page_data": [],
    }
    if lang is None:
        lang = ocr_engine.detect_language(os.path.basename(filepath))
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(filepath), "extracted")
    os.makedirs(output_dir, exist_ok=True)
    doc = pdf_loader.load_pdf(filepath)
    result["page_count"] = len(doc)
    scanned = force_ocr or pdf_loader.is_scanned(doc)
    result["scanned"] = scanned
    if scanned:
        result["method"] = "ocr"
        for pn in range(len(doc)):
            text = ocr_engine.ocr_page(doc, pn, lang, dpi)
            pd = {"page": pn+1, "text": text.strip(), "char_count": len(text.strip()), "method": "ocr"}
            result["pages"].append(pd)
            result["_page_data"].append(pd)
    else:
        result["method"] = "text_extraction"
        pages = pdf_loader.extract_text(doc)
        for p in pages:
            pd = {"page": p["page"], "text": p["text"], "char_count": p["char_count"], "method": "text_extraction"}
            result["pages"].append(pd)
            result["_page_data"].append(pd)
    doc.close()
    full_text = "\n".join(p["text"] for p in result["pages"] if p.get("text"))
    extracted = extractor.extract(full_text)
    result["extracted"] = extracted
    base_name = os.path.splitext(result["filename"])[0]
    result["exports"] = exporter.export_all(result, base_name, output_dir)
    elapsed = (datetime.now() - start).total_seconds()
    result["processing_time_seconds"] = round(elapsed, 2)
    return result

def process_pdf_batch(filepaths, output_dir, lang=None):
    results = []
    for fp in filepaths:
        print(f"Processing: {fp}")
        r = process_pdf(fp, output_dir, lang)
        results.append(r)
        print(f"  Done: {r["page_count"]} pages, {r["method"]}")
    return results
