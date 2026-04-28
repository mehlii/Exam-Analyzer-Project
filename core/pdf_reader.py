import pdfplumber
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

def extract_exam_data(pdf_path: str) -> pd.DataFrame | None:
    """PDF dosyasından tüm sayfalardaki tabloları okuyup birleştirir."""
    if not os.path.isabs(pdf_path):
        pdf_path = os.path.join(os.getcwd(), pdf_path)

    all_data = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_data.append(df)
                else:
                    logger.warning(f"Sayfa {i+1}: tablo bulunamadı, atlanıyor.")

        if not all_data:
            logger.warning("PDF içinde hiç tablo bulunamadı.")
            return None

        return pd.concat(all_data, ignore_index=True)

    except FileNotFoundError:
        logger.error(f"Dosya bulunamadı: {pdf_path}")
        return None
    except Exception as e:
        logger.error(f"Okuma hatası: {e}")
        return None