"""PDFUploadForm testleri — DB ve diğer ekip parçalarına bağımlı değil."""

from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from analysis.forms import MAX_PDF_SIZE, PDFUploadForm

PDF_HEADER = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"


def _pdf_file(name="rapor.pdf", size_bytes=1024, content_type="application/pdf"):
    payload = PDF_HEADER + b"0" * max(0, size_bytes - len(PDF_HEADER))
    return SimpleUploadedFile(name, payload, content_type=content_type)


def test_valid_pdf_passes():
    form = PDFUploadForm(files={"pdf_file": _pdf_file()})
    assert form.is_valid(), form.errors


def test_non_pdf_extension_rejected():
    form = PDFUploadForm(files={"pdf_file": _pdf_file(name="rapor.txt")})
    assert not form.is_valid()
    assert "pdf_file" in form.errors


def test_oversize_file_rejected():
    too_big = MAX_PDF_SIZE + 1024
    form = PDFUploadForm(files={"pdf_file": _pdf_file(size_bytes=too_big)})
    assert not form.is_valid()
    assert "pdf_file" in form.errors
    assert any("büyük" in str(e).lower() for e in form.errors["pdf_file"])


def test_wrong_content_type_rejected():
    form = PDFUploadForm(
        files={"pdf_file": _pdf_file(content_type="image/png")}
    )
    assert not form.is_valid()
    assert "pdf_file" in form.errors


def test_empty_submission_rejected():
    form = PDFUploadForm(data={}, files={})
    assert not form.is_valid()
    assert "pdf_file" in form.errors
