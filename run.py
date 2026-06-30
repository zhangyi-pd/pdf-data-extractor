#!/usr/bin/env python3
"""PDF Data Extractor — CLI entry point."""
import sys, os, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import process_pdf, process_pdf_batch


def main():
    parser = argparse.ArgumentParser(
        description="PDF Data Extractor — Extract structured data from PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    sp = sub.add_parser("scan", help="Process a single PDF")
    sp.add_argument("pdf_path", help="Path to the PDF file")
    sp.add_argument("--output-dir", "-o", default=None)
    sp.add_argument("--lang", "-l", default=None, help="Tesseract lang (eng, chi_sim, ara)")
    sp.add_argument("--force-ocr", "-f", action="store_true")
    sp.add_argument("--verbose", "-v", action="store_true")

    bp = sub.add_parser("batch", help="Process all PDFs in a directory")
    bp.add_argument("input_dir")
    bp.add_argument("--output-dir", "-o", default=None)
    bp.add_argument("--lang", "-l", default=None)

    args = parser.parse_args()

    if args.command == "scan":
        if not os.path.exists(args.pdf_path):
            print(f"Error: File not found: {args.pdf_path}")
            sys.exit(1)
        print(f"Processing: {args.pdf_path}")
        result = process_pdf(args.pdf_path, args.output_dir, args.lang, force_ocr=args.force_ocr)
        _print_summary(result)
        if args.verbose:
            for p in result["pages"]:
                print(f"\n{'='*60}\nPage {p['page']}\n{'='*60}")
                print(p.get("text", "")[:2000])

    elif args.command == "batch":
        if not os.path.isdir(args.input_dir):
            print(f"Error: Directory not found: {args.input_dir}")
            sys.exit(1)
        pdfs = [os.path.join(args.input_dir, f) for f in os.listdir(args.input_dir)
                if f.lower().endswith(".pdf")]
        if not pdfs:
            print(f"No PDFs found in {args.input_dir}")
            sys.exit(1)
        print(f"Found {len(pdfs)} PDFs.")
        results = process_pdf_batch(pdfs, args.output_dir or os.path.join(args.input_dir, "extracted"), args.lang)
        print(f"\nBatch Complete: {len(results)} files")
        for r in results:
            _print_summary(r)
    else:
        parser.print_help()


def _print_summary(result):
    print(f"\n{'='*50}")
    print(f"File: {result['filename']}")
    print(f"Pages: {result['page_count']} | Method: {result['method']} | Time: {result['processing_time_seconds']}s")
    if result.get("exports"):
        for fmt, path in result["exports"].items():
            print(f"  {fmt.upper()}: {path}")
    ext = result.get("extracted", {})
    if ext:
        print(f"  Type: {ext.get('document_type', '?')}")
        fields = {k: v for k, v in ext.items()
                  if not k.startswith("_") and k != "document_type" and not isinstance(v, list)}
        if fields:
            print(f"  Fields: {len(fields)}")
            for k, v in list(fields.items())[:5]:
                print(f"    {k}: {str(v)[:60]}")


if __name__ == "__main__":
    main()
