import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from core.cleaner import clean_dataframe


def test_clean_dataframe_logic():
    dirty_data = pd.DataFrame({
        "0": ["Matematik", "Matematik"],
        "1": ["20", "15"],
        "2": ["0", "5"],
        "3": ["20.0", "13.75"]
    })

    cleaned = clean_dataframe(dirty_data)

    # Aynı ders teke düşmeli
    assert len(cleaned) == 1, f"Beklenen 1 satır, gelen: {len(cleaned)}"

    # Sayısal dönüşüm doğru olmalı
    assert cleaned["Doğru"].iloc[0] == 20.0, f"Beklenen 20.0, gelen: {cleaned['Doğru'].iloc[0]}"

    # Sütun adları doğru olmalı
    assert list(cleaned.columns) == ["Ders", "Soru", "Yanlış", "Doğru"]

    # Yanlış sayısal olmalı
    assert cleaned["Yanlış"].iloc[0] == 0.0

    print("✓ Tüm testler geçti")
    print(cleaned)


if __name__ == "__main__":
    test_clean_dataframe_logic()