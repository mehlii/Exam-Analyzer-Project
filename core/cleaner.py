import pandas as pd

COLUMN_MAP = {
    "0": "Ders",
    "1": "Soru",
    "2": "Yanlış",
    "3": "Doğru",
}

NUMERIC_COLUMNS = ["Soru", "Yanlış", "Doğru"]


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ham DataFrame'i temizler:
      1. Sütunları anlamlı isimlerle yeniden adlandırır.
      2. Sayısal sütunları float'a dönüştürür.
      3. Aynı derse ait tekrarlı satırları kaldırır (ilk geçerli kayıt kalır).
    """
    df = df.copy()

    # 1. Rename
    df = df.rename(columns=COLUMN_MAP)

    # 2. Numeric cast — hatalı değerler NaN olur, sessizce geçer
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 3. Dedup — aynı ders adına göre, ilk temiz satırı tut
    df = df.drop_duplicates(subset=["Ders"], keep="first")

    df = df.reset_index(drop=True)
    return df