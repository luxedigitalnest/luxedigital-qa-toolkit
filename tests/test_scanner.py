from pathlib import Path
from PIL import Image
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
