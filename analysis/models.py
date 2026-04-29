# analysis/models.py
# Türkçe not: Analiz ve puan modelleri.

from django.conf import settings
from django.db import models


class Analysis(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Beklemede"
        PROCESSING = "processing", "İşleniyor"
        COMPLETED = "completed", "Tamamlandı"
        FAILED = "failed", "Hatalı"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analyses",
        verbose_name="Kullanıcı",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Yüklenme zamanı")
    file_name = models.CharField(max_length=255, verbose_name="Dosya adı")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Durum",
    )

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Analiz"
        verbose_name_plural = "Analizler"

    def __str__(self) -> str:
        return f"{self.user} - {self.file_name} ({self.status})"


class Score(models.Model):
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name="scores",
        verbose_name="Analiz",
    )
    subject = models.CharField(max_length=100, verbose_name="Ders")
    score = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Puan")
    exam_date = models.DateField(verbose_name="Sınav tarihi")

    class Meta:
        ordering = ["-exam_date", "subject"]
        verbose_name = "Puan"
        verbose_name_plural = "Puanlar"

    def __str__(self) -> str:
        return f"{self.subject}: {self.score} ({self.exam_date})"
