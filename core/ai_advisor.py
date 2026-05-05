"""Hibrit AI Advisor — Ders bazlı yorum + zayıf konu listesi.

İki kanallı yapı:
  - Birincil: Anthropic Claude API (Haiku 4.5). Ham PDF metni de bağlam olarak alır.
  - Yedek: Kural bazlı şablon. API erişilemediğinde devreye girer.

Tek dış API: `analyze(student_name, summary, subject_scores, raw_text) -> dict`.
Hatalar yakalanır; her zaman aynı şemada bir dict döner (asla raise etmez).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from django.conf import settings

logger = logging.getLogger("analysis.views")  # views ile aynı namespace


# Eşikler — kural bazlı yolda kullanılır
SCORE_HIGH = 75
SCORE_MID = 50

# LGS müfredatına özgü ders → muhtemel konu listesi (rule-based path için)
LGS_TOPICS: dict[str, list[str]] = {
    "Matematik": [
        "Çarpanlara Ayırma", "Cebirsel İfadeler", "Denklemler ve Eşitsizlikler",
        "Üslü Sayılar", "Kareköklü Sayılar", "Olasılık", "Üçgenler",
        "Eşlik ve Benzerlik", "Dönüşümler", "Geometrik Cisimler",
    ],
    "Türkçe": [
        "Sözcükte Anlam", "Cümlede Anlam", "Paragraf",
        "Anlatım Bozuklukları", "Söz Sanatları", "Cümle Türleri",
        "Yazım Kuralları", "Noktalama İşaretleri", "Fiilimsi",
    ],
    "Fen Bilimleri": [
        "DNA ve Genetik Kod", "Mitoz ve Mayoz", "Basınç", "Mevsimler ve İklim",
        "Madde Döngüleri", "Kimyasal Tepkimeler", "Asitler ve Bazlar",
        "Elektrik Yükleri", "Enerji Dönüşümleri",
    ],
    "Sosyal Bilgiler": [
        "Bir Kahraman Doğuyor", "Milli Uyanış", "Milli Bir Destan",
        "Atatürkçülük", "Demokratikleşme", "Atatürk Dönemi Dış Politika",
    ],
    "İngilizce": [
        "Friendship", "Teen Life", "In the Kitchen",
        "On the Phone", "The Internet", "Adventures",
        "Tourism", "Chores", "Science", "Natural Forces",
    ],
    "Din Kültürü": [
        "Kader İnancı", "Zekât ve Sadaka", "Din ve Hayat",
        "Hz. Muhammed'in Örnekliği", "Kur'an-ı Kerim ve Özellikleri",
    ],
}


def analyze(
    student_name: str,
    summary: dict,
    subject_scores: list[dict],
    raw_text: str,
) -> dict:
    """Hibrit yorum üret. AI'yi dener, fail olursa kural bazlı."""
    if _use_ai():
        try:
            result = _ai_analyze(student_name, summary, subject_scores, raw_text)
            if result and result.get("subjects"):
                result["source"] = "ai"
                return result
            logger.warning("AI advisor boş yanıt verdi, rule-based'e düşülüyor")
        except Exception:
            logger.exception("AI advisor çağrısı başarısız, rule-based fallback")

    return _rule_based_analyze(subject_scores)


def _use_ai() -> bool:
    return bool(getattr(settings, "AI_ADVISOR_ENABLED", False)) and bool(
        getattr(settings, "GEMINI_API_KEY", "")
    )


# ---------------------------------------------------------------------------
# AI yolu
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """Sen LGS sınavlarını analiz eden, samimi ve dürüst bir öğretmen asistanısın.
Öğrenciye Türkçe, anlaşılır, motive edici ama dürüst geri bildirim verirsin.
LGS müfredatına özgü konu adları kullanırsın. Her zaman SADECE geçerli JSON döndürürsün."""


def _ai_analyze(
    student_name: str,
    summary: dict,
    subject_scores: list[dict],
    raw_text: str,
) -> dict:
    import google.generativeai as genai  # local import

    genai.configure(api_key=settings.GEMINI_API_KEY)

    subjects_brief = [
        {
            "subject": s.get("subject", ""),
            "score": round(float(s.get("score", 0)), 1),
        }
        for s in subject_scores
    ]
    overall_avg = round(float(summary.get("average", 0)), 1)

    user_prompt = f"""Öğrenci: {student_name or 'Belirtilmemiş'}
Genel ortalama (yüzde): {overall_avg}

Ders bazlı yüzde puanları:
{json.dumps(subjects_brief, ensure_ascii=False, indent=2)}

Ham PDF metni (varsa, yanlış soru başlıklarında konu adları olabilir):
\"\"\"
{raw_text}
\"\"\"

Görev:
Aşağıdaki şemada SADECE geçerli JSON döndür:

{{
  "overall": "2-3 cümle genel değerlendirme",
  "subjects": [
    {{
      "subject": "ders adı (yukarıdakilerle aynı yazım)",
      "commentary": "1-2 cümle ders yorumu",
      "weak_topics": ["konu1", "konu2", "konu3"],
      "priority": "yuksek" | "orta" | "dusuk"
    }}
  ],
  "next_steps": ["3 maddelik somut çalışma önerisi"]
}}

Kurallar:
- Tüm metin Türkçe olmalı.
- weak_topics LGS müfredatına özgü olsun (genel ifadeler değil).
- Skoru ≥%80 olan derslerde priority="dusuk", weak_topics 0-1 madde.
- Skoru %50-%79 ise priority="orta".
- Skoru <%50 ise priority="yuksek", weak_topics en az 3 madde.
- Ham PDF metninde "Yanlış" satırlarında konu varsa onları kullan; yoksa LGS müfredatından en olası konuları seç.
"""

    model = genai.GenerativeModel(
        model_name=getattr(settings, "AI_ADVISOR_MODEL", "gemini-2.5-flash"),
        system_instruction=_SYSTEM_PROMPT,
    )
    resp = model.generate_content(
        user_prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            max_output_tokens=2000,
        ),
        request_options={"timeout": getattr(settings, "AI_ADVISOR_TIMEOUT", 30)},
    )

    text = (resp.text or "").strip()
    return _parse_json(text)


def _parse_json(text: str) -> dict:
    """AI çıktısı saf JSON olmalı; bazen markdown sarabilir veya trailing comma içerebilir."""
    if not text:
        return {}
    # Fenced code-block kaldırma
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1 and last > first:
            text = text[first : last + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Yaygın AI hatalarını temizle ve tekrar dene
        cleaned = re.sub(r",\s*([\]}])", r"\1", text)  # trailing comma
        cleaned = cleaned.replace("“", '"').replace("”", '"')  # smart quotes
        cleaned = cleaned.replace("‘", "'").replace("’", "'")
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("AI JSON parse başarısız (cleaned ile bile)")
            return {}


# ---------------------------------------------------------------------------
# Kural bazlı yol
# ---------------------------------------------------------------------------

def _rule_based_analyze(subject_scores: list[dict]) -> dict:
    if not subject_scores:
        return {
            "overall": "Henüz analiz edilecek veri yok.",
            "subjects": [],
            "next_steps": [],
            "source": "rule",
        }

    items = []
    weak_count = 0
    strong_count = 0
    for entry in subject_scores:
        subject = str(entry.get("subject", ""))
        score = float(entry.get("score", 0))
        priority = _priority_for(score)
        if priority == "yuksek":
            weak_count += 1
        elif priority == "dusuk":
            strong_count += 1

        topic_pool = LGS_TOPICS.get(subject, [])
        if priority == "yuksek":
            topics = topic_pool[:4] if topic_pool else []
        elif priority == "orta":
            topics = topic_pool[:2] if topic_pool else []
        else:
            topics = []

        items.append({
            "subject": subject,
            "commentary": _commentary_for(subject, score),
            "weak_topics": topics,
            "priority": priority,
        })

    total = len(subject_scores)
    avg = sum(float(e.get("score", 0)) for e in subject_scores) / total
    overall = _overall_for(avg, weak_count, strong_count, total)

    return {
        "overall": overall,
        "subjects": items,
        "next_steps": _next_steps_for(items),
        "source": "rule",
    }


def _priority_for(score: float) -> str:
    if score >= SCORE_HIGH:
        return "dusuk"
    if score >= SCORE_MID:
        return "orta"
    return "yuksek"


def _commentary_for(subject: str, score: float) -> str:
    s = round(score, 1)
    if score >= SCORE_HIGH:
        return f"{subject} dersinde %{s} ile çok başarılısın. Bu seviyeyi koruman yeterli."
    if score >= SCORE_MID:
        return f"{subject} dersinde %{s} aldın. Ortalamayı yakalamışsın; eksik konuları tamamlarsan üst seviyeye geçebilirsin."
    return f"{subject} dersinde %{s} alarak hedefin altında kaldın. Bu derse öncelik ver, temel konuları tekrar et."


def _overall_for(avg: float, weak: int, strong: int, total: int) -> str:
    avg_r = round(avg, 1)
    if avg >= SCORE_HIGH:
        return (
            f"Genel performansın çok iyi (%{avg_r}). {strong}/{total} derste güçlüsün. "
            "Bu temponu sürdür."
        )
    if avg >= SCORE_MID:
        return (
            f"Genel ortalama %{avg_r}. Ortalamayı yakalamışsın ama {weak} derste "
            "ciddi geliştirme alanın var. Önceliği bunlara ver."
        )
    return (
        f"Genel ortalama %{avg_r}. Birçok derste temel eksiğin görünüyor. "
        "Endişelenme — düzenli çalışmayla bu hızla toparlanır. Önce temel konulara odaklan."
    )


def _next_steps_for(items: list[dict[str, Any]]) -> list[str]:
    high = [i["subject"] for i in items if i["priority"] == "yuksek"]
    mid = [i["subject"] for i in items if i["priority"] == "orta"]
    steps: list[str] = []
    if high:
        steps.append(f"Öncelikli olarak {', '.join(high[:2])} dersine günde 30 dk ayır.")
    if mid:
        steps.append(f"{', '.join(mid[:2])} derslerinde eksik konularını tarayıp test çöz.")
    steps.append("Her hafta bir deneme sınavı çözüp performansını takip et.")
    return steps[:3]
