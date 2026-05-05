"""PDFUploadForm testleri — DB ve diğer ekip parçalarına bağımlı değil."""

from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from analysis.forms import MAX_PDF_SIZE, PDFUploadForm

PDF_HEADER = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
JPEG_HEADER = b"\xff\xd8\xff\xe0\x00\x10JFIF"
PNG_HEADER = b"\x89PNG\r\n\x1a\n"


def _file(name="rapor.pdf", size_bytes=1024, content_type="application/pdf", header=PDF_HEADER):
    payload = header + b"0" * max(0, size_bytes - len(header))
    return SimpleUploadedFile(name, payload, content_type=content_type)


def test_valid_pdf_passes():
    form = PDFUploadForm(files={"pdf_file": _file()})
    assert form.is_valid(), form.errors


def test_jpeg_passes():
    form = PDFUploadForm(files={"pdf_file": _file(name="karne.jpg", content_type="image/jpeg", header=JPEG_HEADER)})
    assert form.is_valid(), form.errors


def test_png_passes():
    form = PDFUploadForm(files={"pdf_file": _file(name="karne.png", content_type="image/png", header=PNG_HEADER)})
    assert form.is_valid(), form.errors


def test_unsupported_extension_rejected():
    form = PDFUploadForm(files={"pdf_file": _file(name="rapor.txt", content_type="text/plain")})
    assert not form.is_valid()
    assert "pdf_file" in form.errors


def test_doc_extension_rejected():
    form = PDFUploadForm(files={"pdf_file": _file(name="rapor.doc", content_type="application/msword")})
    assert not form.is_valid()
    assert "pdf_file" in form.errors


def test_oversize_file_rejected():
    too_big = MAX_PDF_SIZE + 1024
    form = PDFUploadForm(files={"pdf_file": _file(size_bytes=too_big)})
    assert not form.is_valid()
    assert "pdf_file" in form.errors
    assert any("büyük" in str(e).lower() for e in form.errors["pdf_file"])


def test_unsupported_content_type_rejected():
    # Uzantı kabul edilen ama content-type tehlikeli olan dosya
    form = PDFUploadForm(
        files={"pdf_file": _file(content_type="application/x-msdownload")}
    )
    assert not form.is_valid()
    assert "pdf_file" in form.errors


def test_empty_submission_rejected():
    form = PDFUploadForm(data={}, files={})
    assert not form.is_valid()
    assert "pdf_file" in form.errors
