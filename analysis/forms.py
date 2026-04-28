from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

MAX_PDF_SIZE = 5 * 1024 * 1024  # 5 MB


class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField(
        label="PDF Dosyası",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        help_text="Sınav sonuçları içeren PDF (maksimum 5 MB).",
        widget=forms.ClearableFileInput(attrs={"accept": "application/pdf"}),
    )

    def clean_pdf_file(self):
        pdf = self.cleaned_data["pdf_file"]
        if pdf.size > MAX_PDF_SIZE:
            raise ValidationError(
                f"Dosya çok büyük ({pdf.size / 1024 / 1024:.1f} MB). "
                f"Maksimum {MAX_PDF_SIZE // 1024 // 1024} MB yüklenebilir."
            )
        content_type = getattr(pdf, "content_type", "")
        if content_type and content_type != "application/pdf":
            raise ValidationError(
                f"Sadece PDF dosyası yüklenebilir (alınan: {content_type})."
            )
        return pdf
