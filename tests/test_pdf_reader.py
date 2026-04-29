import pytest
from core.pdf_reader import extract_exam_data

def test_extract_returns_dataframe():
    result = extract_exam_data("kayra_test.pdf")
    assert result is not None, "PDF okuma None döndürmemeli"

def test_extract_has_expected_columns():
    result = extract_exam_data("kayra_test.pdf")
    assert result is not None
    assert len(result.columns) > 0, "Sütun olmalı"
    assert len(result) > 0, "En az 1 satır olmalı"

def test_invalid_path_returns_none():
    result = extract_exam_data("olmayan_dosya.pdf")
    assert result is None, "Geçersiz path None döndürmeli"