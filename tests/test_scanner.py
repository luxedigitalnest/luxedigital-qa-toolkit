from pathlib import Path

from PIL import Image
from pypdf import PdfWriter

from luxedigital_qa.scanner import scan_path


def test_empty_file_is_error(tmp_path: Path):
    (tmp_path / "empty.png").write_bytes(b"")
    result = scan_path(tmp_path)
    assert result.errors == 1
    assert any(f.code == "EMPTY_FILE" for f in result.findings)


def test_small_image_warning(tmp_path: Path):
    Image.new("RGB", (500, 500)).save(tmp_path / "small.png")
    assert any(f.code == "LOW_IMAGE_RESOLUTION" for f in scan_path(tmp_path).findings)


def test_good_image_passes_resolution(tmp_path: Path):
    Image.new("RGB", (2400, 3000)).save(tmp_path / "print.png")
    assert not any(f.code == "LOW_IMAGE_RESOLUTION" for f in scan_path(tmp_path).findings)


def test_duplicate_content(tmp_path: Path):
    content = b"x" * 100
    (tmp_path / "one.txt").write_bytes(content)
    (tmp_path / "two.txt").write_bytes(content)
    assert any(f.code == "DUPLICATE_CONTENT" for f in scan_path(tmp_path).findings)


def test_valid_pdf_reports_summary(tmp_path: Path):
    pdf = tmp_path / "guide.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)  # US Letter at 72 points/inch
    with pdf.open("wb") as stream:
        writer.write(stream)
    result = scan_path(tmp_path)
    assert not any(f.code == "BROKEN_PDF" for f in result.findings)
    assert any(f.code == "PDF_SUMMARY" for f in result.findings)


def test_broken_pdf_is_error(tmp_path: Path):
    (tmp_path / "broken.pdf").write_bytes(b"not a real pdf" * 10)
    result = scan_path(tmp_path)
    assert any(f.code == "BROKEN_PDF" for f in result.findings)


def test_svg_missing_viewbox_warns(tmp_path: Path):
    (tmp_path / "art.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100"/></svg>',
        encoding="utf-8",
    )
    result = scan_path(tmp_path)
    assert any(f.code == "SVG_MISSING_VIEWBOX" for f in result.findings)


def test_valid_svg_passes_parse_and_viewbox(tmp_path: Path):
    (tmp_path / "art.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>',
        encoding="utf-8",
    )
    result = scan_path(tmp_path)
    assert not any(f.code in {"BROKEN_SVG", "SVG_MISSING_VIEWBOX", "SVG_INVALID_VIEWBOX"} for f in result.findings)


def test_embedded_raster_in_svg_warns(tmp_path: Path):
    (tmp_path / "mixed.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><image href="preview.png" width="100" height="100"/></svg>',
        encoding="utf-8",
    )
    result = scan_path(tmp_path)
    assert any(f.code == "SVG_EMBEDDED_RASTER" for f in result.findings)
