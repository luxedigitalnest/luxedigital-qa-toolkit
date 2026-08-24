from __future__ import annotations
import argparse
from .scanner import scan_path
from .report import write_json, write_markdown

def build_parser():
    parser = argparse.ArgumentParser(prog="ldqa", description="Quality-check a digital-product delivery folder or ZIP.")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="Scan a folder or ZIP package.")
    scan.add_argument("source")
    scan.add_argument("--report", default=None)
    scan.add_argument("--json-report", default=None)
    scan.add_argument("--max-file-mb", type=float, default=20.0)
    scan.add_argument("--max-package-mb", type=float, default=100.0)
    scan.add_argument("--min-image-px", type=int, default=2000)
    return parser

def main():
    args = build_parser().parse_args()
    summary = scan_path(args.source, max_file_mb=args.max_file_mb, max_package_mb=args.max_package_mb, min_image_px=args.min_image_px)
    print("LuxeDigital QA Toolkit")
    print(f"Files scanned: {summary.files_scanned}")
    print(f"Errors: {summary.errors}")
    print(f"Warnings: {summary.warnings}")
    print(f"Passed checks: {summary.passed_checks}")
    for f in summary.findings:
        print(f"{f.level:5} {f.code:24} {f.path}\n      {f.message}")
    if args.report: write_markdown(summary, args.report)
    if args.json_report: write_json(summary, args.json_report)
    return 1 if summary.errors else 0

if __name__ == "__main__": raise SystemExit(main())
