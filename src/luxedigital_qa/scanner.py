from __future__ import annotations

import hashlib
import re
import tempfile
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

from PIL import Image, UnidentifiedImageError

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
SAFE_NAME = re.compile(r"^[A-Za-z0-9._()\- ]+$")

@dataclass
class Finding:
    level: str
    code: str
    path: str
    message: str
    def to_dict(self): return asdict(self)

@dataclass
class ScanSummary:
    source: str
    files_scanned: int
    total_bytes: int
    errors: int
    warnings: int
    passed_checks: int
    findings: list[Finding]
    def to_dict(self):
        d = asdict(self)
        d["findings"] = [f.to_dict() for f in self.findings]
        return d

def _iter_files(root: Path) -> Iterable[Path]:
    return (p for p in root.rglob("*") if p.is_file())

def _extract_zip_safely(source: Path, dest: Path) -> None:
    with zipfile.ZipFile(source) as zf:
        for member in zf.infolist():
            target = (dest / member.filename).resolve()
            if not str(target).startswith(str(dest.resolve())):
                raise ValueError(f"Unsafe ZIP path: {member.filename}")
        zf.extractall(dest)

def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def scan_path(source: str | Path, *, max_file_mb: float = 20.0, max_package_mb: float = 100.0, min_image_px: int = 2000) -> ScanSummary:
    source = Path(source).expanduser().resolve()
    if not source.exists(): raise FileNotFoundError(source)
    temp = None
    scan_root = source
    if source.is_file():
        if source.suffix.lower() != ".zip": raise ValueError("Source must be a directory or ZIP file.")
        temp = tempfile.TemporaryDirectory(prefix="ldqa-")
        scan_root = Path(temp.name)
        _extract_zip_safely(source, scan_root)
    files = sorted(_iter_files(scan_root))
    findings, passed, total_bytes = [], 0, 0
    names_seen, hashes_seen = {}, {}
    for path in files:
        rel = path.relative_to(scan_root).as_posix()
        size = path.stat().st_size
        total_bytes += size
        if size == 0: findings.append(Finding("ERROR", "EMPTY_FILE", rel, "File is empty. Re-export or remove it."))
        else: passed += 1
        if 0 < size < 64: findings.append(Finding("WARN", "TINY_FILE", rel, f"File is only {size} bytes; verify the export."))
        else: passed += 1
        if size > max_file_mb * 1024 * 1024: findings.append(Finding("WARN", "LARGE_FILE", rel, f"File exceeds {max_file_mb:g} MB."))
        else: passed += 1
        if len(Path(rel).parts) - 1 > 2: findings.append(Finding("WARN", "DEEP_NESTING", rel, "File is nested more than two folders deep."))
        else: passed += 1
        name = path.name
        if not SAFE_NAME.match(name) or "  " in name: findings.append(Finding("WARN", "FILENAME_FORMAT", rel, "Use simple, descriptive filenames with standard characters."))
        else: passed += 1
        lowered = name.lower()
        if lowered in names_seen: findings.append(Finding("WARN", "DUPLICATE_NAME", rel, f"Same filename also appears at {names_seen[lowered]}."))
        else: names_seen[lowered] = rel; passed += 1
        if size > 0:
            digest = _hash_file(path)
            if digest in hashes_seen: findings.append(Finding("WARN", "DUPLICATE_CONTENT", rel, f"Identical content also appears at {hashes_seen[digest]}."))
            else: hashes_seen[digest] = rel; passed += 1
        if path.suffix.lower() in IMAGE_SUFFIXES:
            try:
                with Image.open(path) as im: width, height = im.size
                if min(width, height) < min_image_px: findings.append(Finding("WARN", "LOW_IMAGE_RESOLUTION", rel, f"{width}x{height} px; shortest side is below {min_image_px}px."))
                else: passed += 1
                print_w, print_h = width / 300, height / 300
                if min(print_w, print_h) < 5: findings.append(Finding("WARN", "SMALL_300DPI_PRINT", rel, f"At 300 DPI this is approximately {print_w:.1f}x{print_h:.1f} inches."))
                else: passed += 1
            except (UnidentifiedImageError, OSError): findings.append(Finding("ERROR", "BROKEN_IMAGE", rel, "Image could not be opened by Pillow."))
    if total_bytes > max_package_mb * 1024 * 1024: findings.append(Finding("WARN", "LARGE_PACKAGE", source.name, f"Package exceeds {max_package_mb:g} MB."))
    else: passed += 1
    result = ScanSummary(str(source), len(files), total_bytes, sum(f.level == "ERROR" for f in findings), sum(f.level == "WARN" for f in findings), passed, findings)
    if temp is not None: temp.cleanup()
    return result
