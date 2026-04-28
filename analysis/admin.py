# analysis/admin.py
# Türkçe not: Admin ekranı ayarları.

from django.contrib import admin

from .models import Analysis, Score


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "file_name", "status", "uploaded_at")
    list_filter = ("status", "uploaded_at")
    search_fields = ("file_name", "user__username")
    ordering = ("-uploaded_at",)


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ("id", "analysis", "subject", "score", "exam_date")
    list_filter = ("subject", "exam_date")
    search_fields = ("subject", "analysis__file_name", "analysis__user__username")
    ordering = ("-exam_date",)

