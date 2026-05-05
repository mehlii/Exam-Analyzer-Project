"""
analysis.views — Nisa Apaydın

Pipeline orkestratörü: PDF yükle → core'u çağır → DB'ye yaz → kullanıcıya göster.

Domain adapter notu: Mehlika'nın çıktısı (Türkçe kolonlar: Ders/Soru/Yanlış/Doğru)
ile İdil'in beklediği kanonik şema (subject/score/exam_date) farklı; aşağıdaki
upload_view içinde adapter ile köprü kuruluyor.
"""

import json
import logging
from datetime import date
from pathlib import Path

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from analysis.forms import PDFUploadForm
from analysis.models import Analysis, Score
from core.ai_advisor import analyze as ai_analyze
from core.analyzer import compute_summary
from core.pdf_reader import extract_exam_data
from core.predictor import predict_next_score
from core.vision_extractor import extract_via_vision

logger = logging.getLogger("analysis.views")

HISTORY_PAGE_SIZE = 10
DASHBOARD_RECENT_SCORES = 5

CHART_BG = "rgba(54, 162, 235, 0.5)"
CHART_BORDER = "rgba(54, 162, 235, 1)"


def home_view(request):
    if request.user.is_authenticated:
        return redirect("analysis:dashboard")
    return render(request, "analysis/home.html")


@login_required
def dashboard_view(request):
    latest = (
        Analysis.objects.filter(user=request.user)
        .order_by("-uploaded_at")
        .first()
    )
    context = {"latest": latest}
    if latest is not None:
        context.update(
            {
                "analysis": latest,
                "summary": _normalize_summary(latest.summary_json or {}),
                "recent_scores": list(latest.scores.all()[:DASHBOARD_RECENT_SCORES]),
                "chart_data_json": json.dumps(_build_chart_data(latest)),
            }
        )
    return render(request, "analysis/dashboard.html", context)


@login_required
def upload_view(request):
    if request.method != "POST":
        return render(request, "analysis/upload.html", {"form": PDFUploadForm()})

    form = PDFUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, "analysis/upload.html", {"form": form})

    pdf = form.cleaned_data["pdf_file"]
    logger.info("PDF yükleme: user=%s file=%s size=%d", request.user, pdf.name, pdf.size)

    analysis = Analysis.objects.create(
        user=request.user,
        pdf_file=pdf,
        file_name=pdf.name,
        status=Analysis.Status.PROCESSING,
    )

    # DEMO MODE: pipeline'ı bypass et, sabit LGS karnesini göster.
    from django.conf import settings as _settings
    if getattr(_settings, "DEMO_MODE", False):
        import time
        from core.demo_data import populate_demo_analysis
        populate_demo_analysis(analysis)
        # Loading animasyonunun görünmesi için suni gecikme — UX için.
        time.sleep(4.0)
        logger.info("DEMO MODE: sabit karne ile dolduruldu (analysis=%s)", analysis.pk)
        messages.success(request, "Analysis completed successfully.")
        return redirect("analysis:detail", pk=analysis.pk)

    try:
        ext = Path(pdf.name).suffix.lower().lstrip(".")
        is_pdf = ext == "pdf"

        df_raw = None
        df_canonical = pd.DataFrame()
        extraction_method = "text"

        # PDF için önce hızlı text yolu
        if is_pdf:
            df_raw = extract_exam_data(analysis.pdf_file.path)
            df_canonical = _to_canonical(df_raw) if df_raw is not None else pd.DataFrame()

        # Boşsa veya zaten image ise Vision'a düş
        ai_enabled = getattr(_settings, "AI_ADVISOR_ENABLED", False)
        if df_canonical.empty:
            if ai_enabled:
                if is_pdf:
                    logger.info("Text extraction boş — Vision fallback'e geçiliyor")
                else:
                    logger.info("Image dosyası — doğrudan Vision'a gönderiliyor (.%s)", ext)
                df_vision = extract_via_vision(analysis.pdf_file.path)
                if df_vision is not None and not df_vision.empty:
                    df_raw = df_vision
                    df_canonical = _to_canonical(df_raw)
                    extraction_method = "vision"

        if df_canonical.empty:
            if not ai_enabled and not is_pdf:
                raise ValueError(
                    "Image files require Gemini AI support. The GEMINI_API_KEY "
                    "environment variable is not set. Start the server with "
                    "'GEMINI_API_KEY=... python manage.py runserver' or upload a "
                    "text-based PDF instead."
                )
            if not ai_enabled:
                raise ValueError(
                    "Could not extract a text table from the PDF (it may be "
                    "scanned/image-based). Set GEMINI_API_KEY to enable AI support."
                )
            raise ValueError(
                "Could not extract data from the file. Image quality may be too "
                "low or the table format may differ from what's expected. Try a "
                "clearer photo."
            )

        summary_raw = compute_summary(df_canonical)
        summary = _normalize_summary(summary_raw)

        try:
            predicted, r2 = predict_next_score(df_canonical)
        except Exception:
            logger.exception("Tahmin başarısız (yetersiz veri olabilir)")
            predicted, r2 = None, None

        try:
            ai_advice = ai_analyze(
                student_name=str(summary_raw.get("student_name", "")),
                summary=summary_raw,
                subject_scores=df_canonical[["subject", "score"]].to_dict("records"),
                raw_text=df_raw.to_string()[:3000],
            )
        except Exception:
            logger.exception("AI advisor tamamen başarısız")
            ai_advice = {}
        summary_raw["ai_advice"] = ai_advice
        summary_raw["extraction_method"] = extraction_method

        Score.objects.bulk_create([
            Score(
                analysis=analysis,
                subject=row["subject"],
                score=float(row["score"]),
                exam_date=_as_date(row.get("exam_date")),
            )
            for _, row in df_canonical.iterrows()
        ])

        analysis.summary_json = summary_raw
        analysis.predicted_score = predicted
        analysis.r2_score = r2
        analysis.status = Analysis.Status.COMPLETED
        analysis.save()

        logger.info("Analiz tamamlandı: id=%s scores=%d", analysis.pk, len(df_canonical))
        messages.success(request, "Analysis completed successfully.")
        return redirect("analysis:detail", pk=analysis.pk)

    except Exception as exc:
        logger.exception("Pipeline hatası")
        analysis.status = Analysis.Status.FAILED
        analysis.save(update_fields=["status"])
        messages.error(request, f"Analysis failed: {exc}")
        return redirect("analysis:dashboard")


@login_required
def history_view(request):
    qs = Analysis.objects.filter(user=request.user).order_by("-uploaded_at")
    paginator = Paginator(qs, HISTORY_PAGE_SIZE)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "analysis/history.html", {"page": page})


@login_required
def detail_view(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk, user=request.user)
    scores = list(analysis.scores.all())
    return render(
        request,
        "analysis/detail.html",
        {
            "analysis": analysis,
            "scores": scores,
            "summary": _normalize_summary(analysis.summary_json or {}),
            "chart_data_json": json.dumps(_build_chart_data(analysis)),
        },
    )


def _as_date(v):
    """Pandas Timestamp / datetime.date / None için tek bir DateField uyumlu değer döndürür."""
    if v is None:
        return None
    if hasattr(v, "date") and not isinstance(v, date):
        return v.date()
    return v


def _normalize(s: str) -> str:
    """Türkçe karakterleri ASCII'leştirir; pdfplumber bazen � üretiyor — ona da hazırız."""
    if s is None:
        return ""
    s = str(s).lower()
    table = str.maketrans({
        "ı": "i", "İ": "i", "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g",
        "ç": "c", "Ç": "c", "ö": "o", "Ö": "o", "ü": "u", "Ü": "u",
        "�": "",  # mojibake replacement char
    })
    return s.translate(table)


def _matches(text: str, *needles: str) -> bool:
    """Normalize edilmiş text içinde verilen anahtarlardan herhangi biri var mı?

    Anahtarın da Türkçe formu olabilir; ikisini de normalize edip karşılaştırır.
    """
    norm = _normalize(text)
    return any(_normalize(n) in norm for n in needles)


def _to_canonical(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Ham PDF DataFrame'ini kanonik (subject, score, exam_date) şemasına çevirir.

    DataFrame içinde "Ders/Soru/Doğru" başlık satırını arar (Türkçe karakter veya ASCII
    fallback ile); sonrasındaki veri satırlarını ders/soru/doğru olarak ayrıştırır.

    Kural: score = (Doğru / Soru) * 100 (yüzde başarı). PDF'te tarih yoksa bugünün tarihi.
    """
    empty = pd.DataFrame(columns=["subject", "score", "exam_date"])

    # 1) Ders + Doğru + Soru anahtarlarını içeren satır = header
    header_idx = None
    for idx in range(len(df_raw)):
        row_text = " ".join(str(v) for v in df_raw.iloc[idx].values if v is not None)
        if _matches(row_text, "ders") and _matches(row_text, "doğru", "dogru") and _matches(row_text, "soru"):
            header_idx = idx
            break

    if header_idx is None:
        # Belki kolonların kendisi headers (Mehlika'nın orijinal varsayımı)
        cols_text = " ".join(str(c) for c in df_raw.columns)
        if _matches(cols_text, "ders") and _matches(cols_text, "doğru", "dogru"):
            data = df_raw.copy()
            headers = [str(c) for c in df_raw.columns]
        else:
            return empty
    else:
        headers = [str(v) if v is not None else f"col{i}" for i, v in enumerate(df_raw.iloc[header_idx].values)]
        data = df_raw.iloc[header_idx + 1 :].copy()
        data.columns = headers

    # 2) Hangi kolon ders, hangisi soru/doğru?
    def _find_col(*needles: str):
        for c in data.columns:
            if _matches(c, *needles):
                return c
        return None

    ders_col = _find_col("ders")
    soru_col = _find_col("soru")
    dogru_col = _find_col("doğru", "dogru")
    if ders_col is None or soru_col is None or dogru_col is None:
        return empty

    import numpy as np
    soru = pd.to_numeric(data[soru_col], errors="coerce")
    dogru = pd.to_numeric(data[dogru_col], errors="coerce")
    score = (dogru / soru * 100).replace([np.inf, -np.inf], np.nan).round(2)

    out = pd.DataFrame({
        "subject": data[ders_col].astype(str).str.strip(),
        "score": score,
        "exam_date": [pd.Timestamp.today().normalize()] * len(data),
    }).dropna(subset=["subject", "score"])
    out = out[out["subject"].str.len() > 0]
    out = out[~out["subject"].str.lower().isin({"ders", "nan", "none", ""})]
    return out.reset_index(drop=True)


def _normalize_summary(raw: dict) -> dict:
    """İdil'in döndürdüğü {average, max_score, min_score, subject_averages} sözlüğünü
    template'lerin beklediği {mean, max, min, by_subject} şemasına eşler."""
    if not raw:
        return {}
    return {
        "mean": raw.get("average", raw.get("mean", 0)),
        "max": raw.get("max_score", raw.get("max", 0)),
        "min": raw.get("min_score", raw.get("min", 0)),
        "by_subject": raw.get("subject_averages", raw.get("by_subject", {})),
    }


_LABEL_SHORTCUTS = {
    "Religious Studies and Ethics": "Religious Studies",
    "Turkish History and Reforms": "History",
    "Din Kültürü ve Ahlak Bilgisi": "Religious Studies",
    "T.C. İnkılap Tarihi ve Atatürkçülük": "History",
    "Fen Bilimleri": "Science",
}


def _shorten_label(name: str) -> str:
    """Uzun ders adlarını grafik için kısaltır; tablolar tam adı kullanmaya devam eder."""
    return _LABEL_SHORTCUTS.get(name, name)


def _build_chart_data(analysis) -> dict:
    """Chart.js-ready format döner: {labels: [...], datasets: [{label, data, backgroundColor}]}.

    Sema'nın dashboard.html ve detail.html'deki ``data: chartData`` kullanımına uyumlu.
    """
    by_subject: dict[str, list[float]] = {}
    for s in analysis.scores.all():
        by_subject.setdefault(s.subject, []).append(float(s.score))

    labels = [_shorten_label(name) for name in by_subject.keys()]
    averages = [round(sum(v) / len(v), 2) for v in by_subject.values()]

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Subject Average",
                "data": averages,
                "backgroundColor": CHART_BG,
                "borderColor": CHART_BORDER,
                "borderWidth": 1,
            }
        ],
    }
