# analysis/views.py
# Türkçe not: Analiz geçmişi ve detay ekranları.

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Analysis


@login_required
def history(request):
    # Türkçe not: Kullanıcı sadece kendi analizlerini görür.
    analyses = (
        Analysis.objects.filter(user=request.user)
        .prefetch_related("scores")
        .order_by("-uploaded_at")
    )
    return render(request, "analysis/history.html", {"analyses": analyses})


@login_required
def detail(request, pk: int):
    # Türkçe not: Kullanıcı sadece kendi analizine erişebilir.
    analysis = get_object_or_404(
        Analysis.objects.prefetch_related("scores"), pk=pk, user=request.user
    )
    return render(request, "analysis/detail.html", {"analysis": analysis})

