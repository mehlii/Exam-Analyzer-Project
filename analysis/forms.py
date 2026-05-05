from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

MAX_PDF_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"]
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField(
        label="Exam Document",
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        help_text="A PDF or report card photo (JPEG/PNG) containing exam results, max 5 MB.",
        widget=forms.ClearableFileInput(
            attrs={"accept": "application/pdf,image/jpeg,image/png"}
        ),
    )

    def clean_pdf_file(self):
        pdf = self.cleaned_data["pdf_file"]
        if pdf.size > MAX_PDF_SIZE:
            raise ValidationError(
                f"File is too large ({pdf.size / 1024 / 1024:.1f} MB). "
                f"Maximum allowed is {MAX_PDF_SIZE // 1024 // 1024} MB."
            )
        content_type = getattr(pdf, "content_type", "")
        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise ValidationError(
                f"Only PDF, JPEG, or PNG files are allowed (received: {content_type})."
            )
        return pdf
