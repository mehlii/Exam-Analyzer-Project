"""
analysis.views — Nisa Apaydın

Sistemin pipeline orkestratörü: PDF yükle → core'u çağır → DB'ye yaz → kullanıcıya göster.

Aşağıdaki import'lar ekip arkadaşları kendi parçalarını landlemeden ImportError verir:
- core.* modülleri Mehlika ve İdil tarafından yazılacak.
- analysis.models içindeki Analysis ve Score Güler tarafından tanımlanacak.

Beklenen arayüzler plan dökümanında ("Interface Contracts" bölümü) belgelenmiştir.
"""

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from analysis.forms import PDFUploadForm
from analysis.models import Analysis, Score
from core.analyzer import compute_summary
from core.cleaner import clean_dataframe
from core.pdf_reader import extract_tables
from core.predictor import predict_next_score

logger = logging.getLogger("analysis.views")

HISTORY_PAGE_SIZE = 10
DASHBOARD_RECENT_SCORES = 5


def home_view(request):
    """Public landing page."""
    if request.user.is_authenticated:
        return redirect("analysis:dashboard")
    return render(request, "analysis/home.html")


@login_required
def dashboard_view(request):
    """Kullanıcının en son analizini özet + grafik olarak gösterir."""
    latest = (
        Analysis.objects.filter(user=request.user)
        .order_by("-uploaded_at")
        .first()
    )

    context = {"latest": latest}

    if latest is not None:
        recent_scores = list(latest.scores.all()[:DASHBOARD_RECENT_SCORES])
        context.update(
            {
                "summary": latest.summary_json or {},
                "recent_scores": recent_scores,
                "chart_data_json": json.dumps(_build_chart_data(latest)),
            }
        )

    return render(request, "analysis/dashboard.html", context)


@login_required
def upload_view(request):
    """PDF yükle → core pipeline → DB → detay sayfasına yönlendir."""
    if request.method != "POST":
        return render(request, "analysis/upload.html", {"form": PDFUploadForm()})

    form = PDFUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, "analysis/upload.html", {"form": form})

    pdf = form.cleaned_data["pdf_file"]
    logger.info("PDF yükleme: user=%s file=%s size=%d", request.user, pdf.name, pdf.size)

    try:
        rows = extract_tables(pdf)
    except Exception:
        logger.exception("PDF okuma başarısız")
        messages.error(request, "PDF dosyası okunamadı. Dosyanın bozuk olmadığından emin olun.")
        return render(request, "analysis/upload.html", {"form": form})

    try:
        df = clean_dataframe(rows)
    except Exception:
        logger.exception("Veri temizleme başarısız")
        messages.error(request, "PDF içeriği işlenemedi. Tablo formatı beklenenden farklı olabilir.")
        return render(request, "analysis/upload.html", {"form": form})

    if df.empty:
        messages.error(request, "PDF'ten geçerli sınav verisi çıkarılamadı.")
        return render(request, "analysis/upload.html", {"form": form})

    try:
        summary = compute_summary(df)
    except Exception:
        logger.exception("İstatistik hesaplama başarısız")
        messages.error(request, "İstatistikler hesaplanamadı.")
        return render(request, "analysis/upload.html", {"form": form})

    try:
        predicted, r2 = predict_next_score(df)
    except Exception:
        logger.exception("Tahmin başarısız (yetersiz veri olabilir)")
        predicted, r2 = None, None
        messages.warning(
            request,
            "Tahmin modeli çalıştırılamadı (yeterli geçmiş veri yok). Analiz özet ile devam ediyor.",
        )

    pdf.seek(0)
    analysis = Analysis.objects.create(
        user=request.user,
        pdf_file=pdf,
        summary_json=summary,
        predicted_score=predicted,
        r2_score=r2,
        student_name=summary.get("student_name", ""),
    )

    score_objs = [
        Score(
            analysis=analysis,
            subject=row["subject"],
            score=float(row["score"]),
            exam_date=row.get("exam_date") or None,
        )
        for _, row in df.iterrows()
    ]
    Score.objects.bulk_create(score_objs)

    logger.info("Analiz kaydedildi: id=%s scores=%d", analysis.pk, len(score_objs))
    messages.success(request, "Analiz başarıyla tamamlandı.")
    return redirect("analysis:detail", pk=analysis.pk)


@login_required
def history_view(request):
    """Kullanıcının tüm analizleri (sayfalanmış)."""
    qs = Analysis.objects.filter(user=request.user).order_by("-uploaded_at")
    paginator = Paginator(qs, HISTORY_PAGE_SIZE)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "analysis/history.html", {"page": page})


@login_required
def detail_view(request, pk):
    """Tek bir analizin detayı. Başkasının analizine 404."""
    analysis = get_object_or_404(Analysis, pk=pk, user=request.user)
    scores = list(analysis.scores.all())
    return render(
        request,
        "analysis/detail.html",
        {
            "analysis": analysis,
            "scores": scores,
            "summary": analysis.summary_json or {},
            "chart_data_json": json.dumps(_build_chart_data(analysis)),
        },
    )


def _build_chart_data(analysis):
    """Chart.js için subject bazlı bar + zaman bazlı çizgi verisi üretir."""
    scores = list(analysis.scores.all())
    by_subject = {}
    timeline = []
    for s in scores:
        by_subject.setdefault(s.subject, []).append(s.score)
        if s.exam_date is not None:
            timeline.append({"date": s.exam_date.isoformat(), "score": s.score, "subject": s.subject})

    bar = {
        "labels": list(by_subject.keys()),
        "data": [sum(v) / len(v) for v in by_subject.values()],
    }
    timeline.sort(key=lambda r: r["date"])
    return {"bar": bar, "timeline": timeline}
