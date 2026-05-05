"""Görsel PDF Fallback — Claude Vision ile karne tablosu çıkarımı.

`extract_via_vision(pdf_path)` PDF sayfalarını görüntüye çevirir, Claude'a
gönderir ve `[{Ders, Soru, Doğru, Yanlış}, ...]` JSON yapısını döndüren
DataFrame'e dönüştürür. `_to_canonical` ile uyumludur.

Hata yakalanır; başarısız durumda None döner. Başarılı çağrıda
`extraction_method=vision` metadata'sı için kullanılan loglar açıktır.
"""

from __future__ import annotations

import io
import json
import logging
import re
from pathlib import Path

import pandas as pd
from django.conf import settings

logger = logging.getLogger("analysis.views")

DEFAULT_MAX_PAGES = 3
RENDER_DPI = 150  # Vision için yeterli çözünürlük; daha yüksek token maliyetini artırır

_SYSTEM_PROMPT = (
    "Sen bir LGS karnesi tablo çıkarıcısın. Verilen sınav karnesi sayfalarından "
    "ders bazlı sayısal verileri çıkarır, SADECE geçerli JSON döndürürsün. "
    "Açıklama, markdown veya kod bloğu eklemezsin."
)

_USER_PROMPT = (
    "Bu sınav karnesi sayfa(ları)nda bir ders performans tablosu var. "
    "Her ders için aşağıdaki alanları içeren bir liste çıkar:\n"
    "  - Ders (string, ders adı, Türkçe)\n"
    "  - Soru (integer, toplam soru sayısı)\n"
    "  - Doğru (integer, doğru sayısı)\n"
    "  - Yanlış (integer, yanlış sayısı)\n\n"
    "Örnek format:\n"
    "[\n"
    "  {\"Ders\": \"Türkçe\", \"Soru\": 20, \"Doğru\": 18, \"Yanlış\": 2},\n"
    "  {\"Ders\": \"Matematik\", \"Soru\": 20, \"Doğru\": 11, \"Yanlış\": 9}\n"
    "]\n\n"
    "Kurallar:\n"
    "- SADECE JSON döndür; başına/sonuna metin ekleme, markdown kod bloğu kullanma.\n"
    "- Sayısal alanlar sayı olmalı (string değil).\n"
    "- Tabloda gözükmeyen veya emin olmadığın derslerden bahsetme.\n"
    "- Toplam/genel satırlarını dahil etme; yalnızca ders bazlı satırlar."
)


IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def extract_via_vision(file_path: str, max_pages: int = DEFAULT_MAX_PAGES) -> pd.DataFrame | None:
    """Görsel kaynaktan (PDF / JPEG / PNG) Gemini Vision ile tablo çıkarır.

    Dosya uzantısına göre dispatch:
      - .pdf  → pypdfium2 ile sayfaları PNG'ye render et
      - .jpg/.jpeg/.png/.webp → dosya bytes'larını doğrudan kullan

    Başarısız durumda None döner.
    """
    if not getattr(settings, "AI_ADVISOR_ENABLED", False):
        logger.info("Vision fallback: AI_ADVISOR_ENABLED kapalı")
        return None

    ext = Path(file_path).suffix.lower().lstrip(".")
    try:
        if ext == "pdf":
            images = _pdf_to_images(file_path, max_pages=max_pages)
        elif ext in IMAGE_EXTENSIONS:
            with open(file_path, "rb") as f:
                images = [f.read()]
        else:
            logger.warning("Vision fallback: desteklenmeyen uzantı: %s", ext)
            return None
    except Exception:
        logger.exception("Vision fallback: dosya yüklenemedi (%s)", ext)
        return None

    if not images:
        logger.warning("Vision fallback: hiç görüntü çıkmadı")
        return None

    try:
        rows = _call_gemini_vision(images)
    except Exception:
        logger.exception("Vision fallback: Gemini API çağrısı başarısız")
        return None

    if not rows:
        logger.warning("Vision fallback: Claude boş liste döndü")
        return None

    df = pd.DataFrame(rows)

    # Mehlika'nın text reader'ı çıktısıyla aynı kolon isimlerini garanti et
    expected_cols = {"Ders", "Soru", "Doğru", "Yanlış"}
    missing = expected_cols - set(df.columns)
    if missing:
        logger.warning("Vision fallback: eksik kolonlar %s", missing)
        return None

    logger.info("Vision fallback: %d satır çıkarıldı", len(df))
    return df


def _pdf_to_images(pdf_path: str, max_pages: int) -> list[bytes]:
    """PDF sayfalarını PNG bytes listesi olarak döndürür."""
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(str(pdf_path))
    n = min(len(pdf), max_pages)
    out: list[bytes] = []
    scale = RENDER_DPI / 72.0  # PDF default = 72 DPI
    for i in range(n):
        page = pdf[i]
        pil_image = page.render(scale=scale).to_pil()
        buf = io.BytesIO()
        pil_image.save(buf, format="PNG", optimize=True)
        out.append(buf.getvalue())
    return out


def _call_gemini_vision(images: list[bytes]) -> list[dict]:
    import google.generativeai as genai
    from PIL import Image

    genai.configure(api_key=settings.GEMINI_API_KEY)

    model = genai.GenerativeModel(
        model_name=getattr(settings, "AI_ADVISOR_MODEL", "gemini-2.5-flash"),
        system_instruction=_SYSTEM_PROMPT,
    )

    parts: list = [_USER_PROMPT]
    for img_bytes in images:
        parts.append(Image.open(io.BytesIO(img_bytes)))

    resp = model.generate_content(
        parts,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            max_output_tokens=2000,
        ),
        request_options={"timeout": getattr(settings, "AI_ADVISOR_TIMEOUT", 30)},
    )

    text = (resp.text or "").strip()
    return _parse_rows(text)


def _parse_rows(text: str) -> list[dict]:
    """Claude'dan gelen text'i ders satırları listesine parse eder.

    Başına/sonuna açıklama gelse veya markdown ile sarsa da yakalar.
    """
    if not text:
        return []

    fenced = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        first = text.find("[")
        last = text.rfind("]")
        if first != -1 and last != -1 and last > first:
            text = text[first : last + 1]

    raw = json.loads(text)
    if not isinstance(raw, list):
        return []

    cleaned: list[dict] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        ders = str(row.get("Ders", "")).strip()
        if not ders:
            continue
        try:
            soru = int(row.get("Soru", 0))
            dogru = int(row.get("Doğru", row.get("Dogru", 0)))
            yanlis = int(row.get("Yanlış", row.get("Yanlis", 0)))
        except (TypeError, ValueError):
            continue
        cleaned.append({
            "Ders": ders,
            "Soru": soru,
            "Doğru": dogru,
            "Yanlış": yanlis,
        })
    return cleaned
