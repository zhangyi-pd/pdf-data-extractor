"""Field Extractor — parse raw OCR/text into structured fields."""
import re

INV_KW = ["invoice", "bill", "receipt", "vendor", "发票"]
CTR_KW = ["contract", "agreement", "party", "clause", "合同", "协议", "terms"]
FRM_KW = ["form", "application", "registration", "填写", "表格"]

def detect_doc_type(text):
    score = {"invoice": 0, "contract": 0, "form": 0}
    for kw in INV_KW:
        if kw in text.lower(): score["invoice"] += 1
    for kw in CTR_KW:
        if kw in text.lower(): score["contract"] += 1
    for kw in FRM_KW:
        if kw in text.lower(): score["form"] += 1
    mx = max(score, key=score.get) if any(score.values()) else "general"
    return mx

def extract_invoice_fields(text):
    data = {}
    m = re.search(r"(?:Invoice|INV|发票)[\s#:]*([A-Z0-9-]+)", text, re.I)
    if m: data["invoice_number"] = m.group(1)
    m = re.search(r"(?:Date|日期|Issue\s*Date)[:\s]*([\d/-]+)", text, re.I)
    if m: data["date"] = m.group(1)
    m = re.search(r"(?:Total|合计|总计|Amount\s*Due)[\s$\u00a5\u00a3\u20ac:]*([\d,]+(?:\.[\d]{2})?)", text, re.I)
    if m: data["total_amount"] = m.group(1)
    return data

def extract_contract_fields(text):
    data = {}
    for label in ["Party A", "甲方", "Seller", "Buyer"]:
        for line in text.split("\n"):
            if label in line:
                for sep in [":", "："]:
                    if sep in line:
                        data[label.lower().replace(" ", "_")] = line.split(sep, 1)[1].strip()
                        break
    return data

def extract_form_fields(text):
    data = {}
    for line in text.split("\n"):
        line = line.strip()
        for sep in [":", "："]:
            if sep in line:
                parts = line.split(sep, 1)
                k = parts[0].strip().lower().replace(" ", "_")
                v = parts[1].strip()
                if k and v and len(k) < 40 and len(v) < 200:
                    data[k] = v
    return data

def extract_table(text):
    rows = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) < 2: return rows
    for sep in ["|", "\t"]:
        if any(sep in l for l in lines):
            headers = [h.strip() for h in lines[0].split(sep) if h.strip()]
            if len(headers) >= 2:
                for line in lines[1:]:
                    cells = [c.strip() for c in line.split(sep) if c.strip()]
                    if len(cells) == len(headers):
                        rows.append(dict(zip(headers, cells)))
                if rows: return rows
    hdrs = re.split(r"\s{2,}", lines[0])
    if len(hdrs) >= 2:
        for line in lines[1:]:
            cells = re.split(r"\s{2,}", line)
            if len(cells) == len(hdrs):
                rows.append(dict(zip(hdrs, cells)))
    return rows

def extract(text, doc_type=None):
    if not doc_type:
        doc_type = detect_doc_type(text)
    data = {"document_type": doc_type}
    if doc_type == "invoice":
        data.update(extract_invoice_fields(text))
    elif doc_type == "contract":
        data.update(extract_contract_fields(text))
    elif doc_type == "form":
        data.update(extract_form_fields(text))
    tbl = extract_table(text)
    if tbl: data["tables"] = tbl
    data["_text_preview"] = text[:500].strip()
    return data
