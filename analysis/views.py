# analysis/views.py
# Türkçe not: Nisa'nın view'ları (merge sonrası import güvenli hale getirildi).

"""
analysis.views — Nisa Apaydın

Sistemin pipeline orkestratörü: PDF yükle → core'u çağır → DB'ye yaz → kullanıcıya göster.

Aşağıdaki import'lar ekip arkadaşları kendi parçalarını landlemeden ImportError verir:
- core.* modülleri Mehlika ve İdil tarafından yazılacak.
- analysis.models içindeki Analysis ve Score Güler tarafından tanımlanacak.
"""

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from analysis.models import Analysis, Score

logger = logging.getLogger("analysis.views")

HISTORY_PAGE_SIZE = 10
DASHBOARD_RECENT_SCORES = 5

try:
    from analysis.forms import PDFUploadForm  # type: ignore
except Exception:  # pragma: no cover
    PDFUploadForm = None

try:
    from core.analyzer import compute_summary  # type: ignore
    from core.cleaner import clean_dataframe  # type: ignore
    from core.pdf_reader import extract_tables  # type: ignore
    from core.predictor import predict_next_score  # type: ignore
except Exception:  # pragma: no cover
    compute_summary = clean_dataframe = extract_tables = predict_next_score = None


def home_view(request):
    if request.user.is_authenticated:
        return redirect("analysis:history")
    return redirect("accounts:login")


@login_required
def dashboard_view(request):
    latest = Analysis.objects.filter(user=request.user).order_by("-uploaded_at").first()
    recent_scores = list(latest.scores.all()[:DASHBOARD_RECENT_SCORES]) if latest else []
    return render(
        request,
        "analysis/detail.html" if latest else "analysis/history.html",
        {"analysis": latest, "scores": recent_scores, "analyses": [latest] if latest else []},
    )


@login_required
def upload_view(request):
    # Türkçe not: Pipeline bağımlılıkları yoksa sayfayı kapat.
    if request.method != "POST":
        if PDFUploadForm is None:
            messages.error(request, "Yükleme formu hazır değil.")
            return redirect("analysis:history")
        return render(request, "analysis/upload.html", {"form": PDFUploadForm()})

    if PDFUploadForm is None:
        return HttpResponseNotAllowed(["GET"])

    form = PDFUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, "analysis/upload.html", {"form": form})

    if extract_tables is None or clean_dataframe is None:
        messages.error(request, "Analiz pipeline bileşenleri hazır değil.")
        return render(request, "analysis/upload.html", {"form": form})

    pdf = form.cleaned_data["pdf_file"]
    logger.info("PDF yükleme: user=%s file=%s size=%d", request.user, pdf.name, pdf.size)

    try:
        rows = extract_tables(pdf)
        df = clean_dataframe(rows)
    except Exception:
        logger.exception("Pipeline başarısız")
        messages.error(request, "Dosya işlenemedi.")
        return render(request, "analysis/upload.html", {"form": form})

    analysis = Analysis.objects.create(user=request.user, file_name=getattr(pdf, "name", "upload.pdf"))

    score_objs = [
        Score(
            analysis=analysis,
            subject=str(row.get("subject", "")),
            score=float(row.get("score", 0)),
            exam_date=row.get("exam_date") or None,
        )
        for _, row in df.iterrows()
    ]
    Score.objects.bulk_create(score_objs)

    messages.success(request, "Analiz kaydedildi.")
    return redirect("analysis:detail", pk=analysis.pk)


@login_required
def history_view(request):
    qs = Analysis.objects.filter(user=request.user).order_by("-uploaded_at")
    paginator = Paginator(qs, HISTORY_PAGE_SIZE)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "analysis/history.html", {"page": page, "analyses": page.object_list})


@login_required
def detail_view(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk, user=request.user)
    scores = list(analysis.scores.all())
    return render(
        request,
        "analysis/detail.html",
        {"analysis": analysis, "scores": scores, "chart_data_json": json.dumps(_build_chart_data(analysis))},
    )


def _build_chart_data(analysis):
    scores = list(analysis.scores.all())
    by_subject = {}
    timeline = []
    for s in scores:
        by_subject.setdefault(s.subject, []).append(float(s.score))
        if s.exam_date is not None:
            timeline.append({"date": s.exam_date.isoformat(), "score": float(s.score), "subject": s.subject})

    bar = {"labels": list(by_subject.keys()), "data": [sum(v) / len(v) for v in by_subject.values()] if by_subject else []}
    timeline.sort(key=lambda r: r["date"])
    return {"bar": bar, "timeline": timeline}


# Türkçe not: Eski isim uyumluluğu
history = history_view
detail = detail_view
