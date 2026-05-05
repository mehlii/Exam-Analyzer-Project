"""LGS sınav sonuç belgesi formatına benzer örnek PDF'ler üretir.

Üretilen PDF'ler kayra_test.pdf formatına yakın:
- Üstte "LGS" başlığı + öğrenci bilgileri
- Çok kolonlu tablo: Ders, Soru, Doğru, Yanlış, Boş, Net, Sınıf Ort., Kurum Ort., Genel Ort.
- Altta toplam puan ve sıralama

Çıktı: examples/ornek_*.pdf
"""

from pathlib import Path
import random
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold")

OUT_DIR = Path(__file__).parent / "examples"
OUT_DIR.mkdir(exist_ok=True)

styles = getSampleStyleSheet()
title_st = ParagraphStyle("title", parent=styles["Title"], fontName="Arial-Bold",
                          fontSize=20, leading=24, alignment=TA_CENTER, spaceAfter=4)
sub_title_st = ParagraphStyle("subtitle", parent=styles["Normal"], fontName="Arial-Bold",
                              fontSize=11, leading=14, alignment=TA_CENTER, spaceAfter=14,
                              textColor=colors.HexColor("#374151"))
info_st = ParagraphStyle("info", parent=styles["Normal"], fontName="Arial",
                         fontSize=9.5, leading=14, spaceAfter=2)
foot_st = ParagraphStyle("foot", parent=styles["Normal"], fontName="Arial",
                         fontSize=9, leading=12, alignment=TA_CENTER, spaceBefore=10,
                         textColor=colors.HexColor("#6b7280"))
score_st = ParagraphStyle("score", parent=styles["Normal"], fontName="Arial-Bold",
                          fontSize=14, leading=18, alignment=TA_CENTER, spaceAfter=6,
                          textColor=colors.HexColor("#1f2937"))


def _net(d, y):
    return round(d - y * 0.25, 2)


def _avg_around(value: float, jitter: float = 2.0) -> float:
    """Sınıf/kurum/genel ortalaması için, değere yakın küçük rastgele sapma."""
    return round(max(0, min(20, value + random.uniform(-jitter, jitter))), 2)


def build_pdf(filename: str, student_name: str, student_no: str, school: str,
              rows: list[tuple[str, int, int, int, int]]):
    """rows: [(Ders, Soru, Doğru, Yanlış, Boş), ...]"""
    path = OUT_DIR / filename
    doc = SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=1.6 * cm, rightMargin=1.6 * cm,
        topMargin=1.6 * cm, bottomMargin=1.6 * cm,
    )
    story = []

    # ==== Üst başlık ====
    story.append(Paragraph("LGS DENEME SINAVI", title_st))
    story.append(Paragraph("SINAV SONUÇ BELGESİ", sub_title_st))

    # ==== Öğrenci bilgileri (2 kolonlu tablo) ====
    info_data = [
        ["Adı Soyadı:", student_name, "Öğrenci No:", student_no],
        ["Okul:", school, "Sınıf:", "8/A"],
        ["Sınav Tarihi:", "12.05.2026", "Sınav Süresi:", "120 dk"],
    ]
    info_t = Table(info_data, colWidths=[2.7 * cm, 6.5 * cm, 2.7 * cm, 5.5 * cm])
    info_t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Arial-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Arial-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Arial"),
        ("FONTNAME", (3, 0), (3, -1), "Arial"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1f2937")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, -1), (-1, -1), 0.4, colors.HexColor("#9ca3af")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(info_t)
    story.append(Spacer(1, 0.5 * cm))

    # ==== Ana sonuç tablosu ====
    # Kolonlar: Ders | Soru | Doğru | Yanlış | Boş | Net | Sınıf Ort. | Kurum Ort. | Genel Ort.
    table_header = [
        "Ders", "Soru", "Doğru", "Yanlış", "Boş", "Net",
        "Sınıf\nOrt.", "Kurum\nOrt.", "Genel\nOrt.",
    ]

    body = [table_header]
    for ders, soru, dogru, yanlis, bos in rows:
        n = _net(dogru, yanlis)
        body.append([
            ders, str(soru), str(dogru), str(yanlis), str(bos),
            f"{n:.2f}".replace(".", ","),
            f"{_avg_around(n - 1.5):.2f}".replace(".", ","),
            f"{_avg_around(n - 3):.2f}".replace(".", ","),
            f"{_avg_around(n - 4):.2f}".replace(".", ","),
        ])

    main_t = Table(body, colWidths=[3.7 * cm, 1.5 * cm, 1.6 * cm, 1.6 * cm, 1.3 * cm,
                                    1.5 * cm, 1.6 * cm, 1.6 * cm, 1.6 * cm])
    main_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Arial"),
        ("FONTNAME", (0, 1), (0, -1), "Arial-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9ca3af")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(main_t)
    story.append(Spacer(1, 0.6 * cm))

    # ==== Toplam puan kutusu ====
    total_q = sum(r[1] for r in rows)
    total_d = sum(r[2] for r in rows)
    total_y = sum(r[3] for r in rows)
    total_b = sum(r[4] for r in rows)
    total_net = sum(_net(r[2], r[3]) for r in rows)
    success_pct = round(total_d / total_q * 100, 1) if total_q else 0

    summary_data = [
        ["Toplam Soru", "Doğru", "Yanlış", "Boş", "Toplam Net", "Başarı"],
        [str(total_q), str(total_d), str(total_y), str(total_b),
         f"{total_net:.2f}".replace(".", ","), f"%{success_pct}"],
    ]
    sum_t = Table(summary_data, colWidths=[2.6 * cm] * 6)
    sum_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Arial-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, 1), 12),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#fef3c7")),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#1f2937")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9ca3af")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(sum_t)

    story.append(Spacer(1, 0.6 * cm))

    # Tahmini puan (LGS PDF'lerinde olur)
    estimated = round(200 + total_net * 5, 1)
    rank = max(1, int(500_000 - success_pct * 4500))
    story.append(Paragraph(f"Tahmini LGS Puanı: <b>{estimated}</b>".replace(".", ","), score_st))
    story.append(Paragraph(f"Tahmini Sıralama: {rank:,}".replace(",", "."), foot_st))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "Bu belge bir deneme sınavı sonuç raporudur. Resmi LGS sonuçları MEB tarafından açıklanır.",
        foot_st,
    ))

    doc.build(story)
    print(f"  OK {path.name}")


# Veri seti — her senaryo bir öğrenci
random.seed(42)  # tekrarlanabilir rastgelelik

# Örnek 1: Başarılı öğrenci
build_pdf(
    "ornek_basarili.pdf",
    student_name="Ahmet Yılmaz",
    student_no="L0023456",
    school="Atatürk Ortaokulu",
    rows=[
        # (Ders, Soru, Doğru, Yanlış, Boş)
        ("Türkçe", 20, 18, 2, 0),
        ("Matematik", 20, 16, 4, 0),
        ("Fen Bilimleri", 20, 19, 1, 0),
        ("Sosyal Bilgiler", 10, 9, 1, 0),
        ("İngilizce", 10, 10, 0, 0),
        ("Din Kültürü", 10, 8, 2, 0),
    ],
)

# Örnek 2: Orta seviye
build_pdf(
    "ornek_orta.pdf",
    student_name="Zeynep Kaya",
    student_no="L0023457",
    school="Cumhuriyet Ortaokulu",
    rows=[
        ("Türkçe", 20, 14, 5, 1),
        ("Matematik", 20, 11, 8, 1),
        ("Fen Bilimleri", 20, 13, 6, 1),
        ("Sosyal Bilgiler", 10, 7, 3, 0),
        ("İngilizce", 10, 6, 4, 0),
        ("Din Kültürü", 10, 7, 3, 0),
    ],
)

# Örnek 3: Gelişim alanı olan
build_pdf(
    "ornek_geliscekuyor.pdf",
    student_name="Mehmet Demir",
    student_no="L0023458",
    school="Yıldız Ortaokulu",
    rows=[
        ("Türkçe", 20, 10, 9, 1),
        ("Matematik", 20, 7, 12, 1),
        ("Fen Bilimleri", 20, 9, 10, 1),
        ("Sosyal Bilgiler", 10, 5, 5, 0),
        ("İngilizce", 10, 4, 5, 1),
        ("Din Kültürü", 10, 6, 4, 0),
    ],
)

# Örnek 4: Çok düşük performans (yanlış ağırlıklı) — neredeyse hepsi yanlış
build_pdf(
    "ornek_zayif.pdf",
    student_name="Ali Aksoy",
    student_no="L0023459",
    school="Mehmetçik Ortaokulu",
    rows=[
        ("Türkçe", 20, 1, 19, 0),
        ("Matematik", 20, 0, 20, 0),
        ("Fen Bilimleri", 20, 2, 18, 0),
        ("Sosyal Bilgiler", 10, 1, 9, 0),
        ("İngilizce", 10, 0, 10, 0),
        ("Din Kültürü", 10, 1, 9, 0),
    ],
)

print(f"\n4 ornek PDF uretildi: {OUT_DIR}")
