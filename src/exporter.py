"""Exporter — export extracted data to JSON, CSV, MD."""
import json, csv, os
from datetime import datetime

def export_json(data, filepath, indent=2):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    return filepath

def export_csv(data, filepath):
    if not data:
        with open(filepath, "w", encoding="utf-8-sig") as f: pass
        return filepath
    fieldnames = sorted(f for row in data for f in row if not f.startswith("_"))
    if not fieldnames: fieldnames = list(data[0].keys())
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows({k: row.get(k, "") for k in fieldnames} for row in data)
    return filepath

def export_markdown(data, filepath=None):
    lines = ["# Document Extraction Report"]
    lines.append(f"Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
    lines.append("")
    lines.append(f"**Type:** {data.get("document_type", "unknown")}")
    lines.append("")
    lines.append("---")
    lines.append("## Extracted Fields")
    lines.append("")
    skip = {"document_type", "_text_preview", "tables", "raw_text", "_source"}
    for k, v in data.items():
        if k in skip or k.startswith("_"): continue
        if isinstance(v, (str, int, float)):
            lines.append(f"- **{k}:** {v}")
    if "tables" in data and data["tables"]:
        lines.extend(["", "---", "## Extracted Tables", ""])
        for i, tbl in enumerate(data["tables"]):
            if isinstance(tbl, dict):
                lines.extend([f"### Table {i+1}", "", "| Field | Value |", "|-------|-------|"])
                for k, v in tbl.items():
                    lines.append(f"| {k} | {v} |")
    if "_text_preview" in data:
        lines.extend(["", "---", "## Raw Text Preview", "", "`", data["_text_preview"][:500], "`", ""])
    output = "\n".join(lines)
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f: f.write(output)
    return output

def export_all(extracted, base_name, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    results = {}
    jp = os.path.join(output_dir, f"{base_name}.json")
    export_json(extracted, jp)
    results["json"] = jp
    mp = os.path.join(output_dir, f"{base_name}.md")
    export_markdown(extracted, mp)
    results["markdown"] = mp
    return results
