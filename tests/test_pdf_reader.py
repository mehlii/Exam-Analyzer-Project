import pytest
from core.pdf_reader import extract_exam_data

def test_extract_exam_data_success():
    # Mevcut test dosyamızla deniyoruz
    result = extract_exam_data("kayra_test.pdf")
    assert result is not None, "PDF okuma sonucu boş dönmemeli!"