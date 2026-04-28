# analysis/admin.py
# Türkçe not: Admin ekranı ayarları.

from django.contrib import admin

from .models import Analysis, Score


class ScoreInline(admin.TabularInline):
    model = Score
    extra = 0
    fields = ("subject", "score", "exam_date")
    ordering = ("-exam_date", "subject")
    show_change_link = True


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "file_name", "status", "uploaded_at", "score_count")
    list_filter = ("status", "uploaded_at")
    search_fields = ("file_name", "user__username", "user__email")
    date_hierarchy = "uploaded_at"
    ordering = ("-uploaded_at",)
    inlines = [ScoreInline]

    @admin.display(description="Skor sayısı")
    def score_count(self, obj: Analysis) -> int:
        return obj.scores.count()


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ("id", "analysis", "subject", "score", "exam_date")
    list_filter = ("subject", "exam_date")
    search_fields = ("subject", "analysis__file_name", "analysis__user__username")
    date_hierarchy = "exam_date"
    ordering = ("-exam_date",)

