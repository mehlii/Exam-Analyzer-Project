# ExamAI — AI-Powered Exam Performance Analyzer

> **YMH210/220 Final Project** · A Django web application that analyzes exam result PDFs / report card photos, generates per-subject AI feedback, and predicts the next exam score using linear regression.

![Stack](https://img.shields.io/badge/Django-5.2-092E20?logo=django) ![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python) ![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google) ![License](https://img.shields.io/badge/License-Academic-blueviolet)

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Architecture](#architecture)
5. [Project Structure](#project-structure)
6. [Installation](#installation)
7. [Environment Variables](#environment-variables)
8. [Usage](#usage)
9. [AI Integration (Google Gemini)](#ai-integration-google-gemini)
10. [Demo Mode](#demo-mode)
11. [Testing](#testing)
12. [Team](#team)

---

## Overview

ExamAI helps students understand their exam performance by automating the entire analysis workflow:

1. **Upload** an exam result PDF (text-based) **or** a report card photo (JPEG/PNG).
2. The system **extracts** the score table — first via `pdfplumber`, then via Gemini Vision OCR as a fallback.
3. It **computes** per-subject statistics, predicts the next exam score with linear regression, and generates **AI tutor feedback** with a detailed study guide.
4. Results are visualized on a dark, glassmorphism dashboard (Bootstrap 5 + Chart.js).

The full pipeline runs **locally** — no exam data leaves the user's machine except for the AI prompt sent to Google Gemini (when enabled).

---

## Features

| Feature | Description |
|---|---|
| **Automated Extraction** | Hybrid pipeline: `pdfplumber` for text-based PDFs, **Gemini Vision** for image-based PDFs / JPEG / PNG. |
| **Per-Subject Analysis** | Computes mean, max, min, and per-subject averages from the canonical exam table. |
| **AI Tutor Feedback** | Per-subject commentary, weak topic tags, and a detailed study guide ("how to study X") for every wrong topic. |
| **Score Prediction** | Linear regression on historical exam scores; outputs predicted next score + R² confidence. |
| **Visual Dashboard** | Dark glassmorphism UI with gradient text, neon highlights, and Chart.js bar charts. |
| **History & Auth** | Per-user analysis history, registration, login, sessions, CSRF-protected forms. |
| **Multi-Format Upload** | Single form accepts PDF, JPEG, and PNG (up to 5 MB). |
| **Feature Flag** | `DEMO_MODE` env flag bypasses the live pipeline with a fixed fixture for safe demos / offline runs. |

---

## Tech Stack

**Backend**
- Django 5.2 (full-stack monolith)
- SQLite + Django ORM
- `pdfplumber`, `pypdfium2` — PDF parsing & rasterization
- `pandas`, `numpy` — data wrangling
- `scikit-learn` — `LinearRegression` for score prediction
- `google-generativeai` — Gemini API (text + vision)
- `python-dotenv` — `.env` loading

**Frontend**
- Bootstrap 5 + custom dark / glassmorphism CSS
- Chart.js (bar charts on dashboard & detail pages)
- Inter font (Google Fonts)

**Testing**
- `pytest`, `pytest-django` (24 tests across forms, urls, views)

---

## Architecture

```
                 ┌─────────────────────┐
   PDF / JPEG ──▶│   upload_view       │
                 │   (analysis/views)  │
                 └──────────┬──────────┘
                            │
              ┌─────────────┴────────────┐
              │   DEMO_MODE check        │
              └─────┬─────────────┬──────┘
                    │ off         │ on
                    ▼             ▼
       ┌────────────────────┐   ┌────────────────────┐
       │ Text Pipeline      │   │ populate_demo_     │
       │ pdfplumber         │   │ analysis           │
       │ → _to_canonical    │   │ (fixed fixture)    │
       └─────────┬──────────┘   └────────┬───────────┘
                 │ empty?                │
                 ▼                       │
       ┌────────────────────┐            │
       │ Vision Pipeline    │            │
       │ pypdfium2 / PIL    │            │
       │ → Gemini Vision    │            │
       │ → _to_canonical    │            │
       └─────────┬──────────┘            │
                 │                       │
                 ▼                       │
       ┌────────────────────┐            │
       │ Analyzer           │            │
       │ - compute_summary  │            │
       │ - predict_next     │            │
       │ - ai_advisor       │◀───────────┘
       └─────────┬──────────┘
                 ▼
       ┌────────────────────┐
       │ Detail page        │
       │ Charts + AI cards  │
       └────────────────────┘
```

### Pipeline Detail

1. **`upload_view`** receives the file, creates an `Analysis` row (`status=PROCESSING`).
2. **Demo flag** check → if on, `populate_demo_analysis` writes a fixed fixture and returns.
3. **Text path**: PDF → `pdfplumber.extract_exam_data` → `_to_canonical` (header detection + Turkish-character normalization).
4. **Vision fallback**: empty result or image input → `extract_via_vision` (Gemini 2.5 Flash Lite) → `_to_canonical`.
5. **Analyzer**: `compute_summary` (mean/max/min), `predict_next_score` (linear regression on history), `ai_analyze` (Gemini advisor with rule-based fallback).
6. `Analysis.summary_json` stores the full result; `Score` rows are bulk-created.

---

## Project Structure

```
exam_analyzer/
├── accounts/                # User registration, login, logout (Django auth-based)
│   ├── forms.py
│   ├── urls.py
│   └── views.py
├── analysis/                # Core analysis app
│   ├── forms.py             # PDFUploadForm (PDF + JPEG + PNG, 5 MB cap)
│   ├── models.py            # Analysis, Score
│   ├── urls.py
│   └── views.py             # upload_view, dashboard_view, detail_view, history_view
├── core/                    # Stateless analysis modules
│   ├── pdf_reader.py        # pdfplumber-based text extraction
│   ├── cleaner.py           # Header + row normalization
│   ├── analyzer.py          # compute_summary
│   ├── predictor.py         # predict_next_score (LinearRegression)
│   ├── ai_advisor.py        # Hybrid Gemini + rule-based advisor
│   ├── vision_extractor.py  # Gemini Vision OCR (PDF & images)
│   └── demo_data.py         # Fixed demo fixture (Beril Yildiz / 8th Grade Practice Exam)
├── exam_analyzer/           # Project config
│   ├── settings.py
│   └── urls.py
├── templates/               # Project-level templates (dark glassmorphism UI)
│   ├── base.html
│   ├── accounts/
│   │   ├── login.html
│   │   └── register.html
│   └── analysis/
│       ├── home.html
│       ├── dashboard.html
│       ├── upload.html      # With "Analyzing..." spinner + progress bar
│       ├── detail.html      # AI Tutor Feedback + Weak Topics study guide
│       └── history.html
├── tests/                   # pytest test suite
│   ├── test_forms.py
│   ├── test_urls.py
│   └── test_views.py
├── examples/                # Sample exam PDFs/images for demos
├── .env.example
├── manage.py
├── pytest.ini
└── requirements.txt
```

---

## Installation

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/mehlii/Exam-Analyzer-Project.git
cd Exam-Analyzer-Project

# 2. Create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy the env template (defaults work for demo)
cp .env.example .env

# 5. Apply database migrations
python manage.py migrate

# 6. (Optional) Create an admin user
python manage.py createsuperuser

# 7. Run the dev server
python manage.py runserver
```

Open **http://localhost:8000/** in your browser.

---

## Environment Variables

Configured via `.env` (auto-loaded by `python-dotenv` in `exam_analyzer/settings.py`):

| Variable | Default | Description |
|---|---|---|
| `DEMO_MODE` | `1` | When `1`, every upload returns the fixed demo fixture. Set to `0` for the live pipeline. |
| `GEMINI_API_KEY` | _(empty)_ | Required only when `DEMO_MODE=0` and you want AI advisor / Vision OCR. Get one at [aistudio.google.com](https://aistudio.google.com/app/apikey). |

`AI_ADVISOR_ENABLED` is auto-derived: `True` when `GEMINI_API_KEY` is set, else `False`.

---

## Usage

### 1. Register / Sign In

Go to `/accounts/register/`, create an account, and sign in.

### 2. Upload an Exam Document

Click **Upload** → choose a PDF or JPEG/PNG photo of an exam report card.
- A loading screen displays 6 pipeline stages (Validating → Vision OCR → Parsing → Linear Regression → AI Feedback → Study Guide).
- Once complete, you're redirected to the **Detail** page.

### 3. Detail Page

- **Overall Average** card with gradient text
- **Next Prediction** card (linear-regression score + R²)
- **Subject-Level Results** table
- **Bar chart** of subject averages (Chart.js)
- **AI Tutor Feedback** section:
  - Overall commentary
  - Per-subject cards with PRIORITY / IMPROVE / STRONG badges
  - Weak topic tags
  - **"Weak Topics — How to Study"** with 1-2 sentence study guidance per topic
  - Numbered "Next Steps" plan

### 4. History

`/analysis/history/` — paginated list of all your analyses with status badges (Completed / Failed / Processing).

---

## AI Integration (Google Gemini)

### Text Advisor (`core/ai_advisor.py`)

A **hybrid advisor** that:
1. Calls **Gemini 2.5 Flash Lite** with a structured prompt asking for JSON output (`response_mime_type=application/json`).
2. Defensively parses the response with `_parse_json` (handles trailing commas, smart quotes).
3. Falls back to a **rule-based advisor** if the API fails or `GEMINI_API_KEY` is missing.

### Vision OCR (`core/vision_extractor.py`)

For image-based PDFs and JPEG/PNG inputs:
1. **PDF** → `pypdfium2` rasterizes each page to a PIL `Image`.
2. **JPEG/PNG** → opened directly via `PIL.Image.open`.
3. Each image is sent to **Gemini Vision** with a prompt asking for a Markdown table of `(subject, total, correct, wrong, score)` rows.
4. The response is parsed back into a pandas DataFrame and merged into the canonical schema.

### Configuration

```python
# exam_analyzer/settings.py
AI_ADVISOR_MODEL = "gemini-2.5-flash-lite"
AI_ADVISOR_TIMEOUT = 60  # seconds
```

---

## Demo Mode

`DEMO_MODE` is a **feature flag** (12-factor app pattern) that ensures deterministic output during demos / presentations even if:
- The Gemini API key is missing or revoked
- The API quota is exceeded
- Network connectivity is unreliable

**When enabled** (`DEMO_MODE=1`), `upload_view` short-circuits to `populate_demo_analysis` (in `core/demo_data.py`), which writes a fixed fixture for **Beril Yildiz / 8th Grade Practice Exam**:

| Subject | Correct | Wrong | Score |
|---|---|---|---|
| Turkish | 12 | 8 | 60% |
| Mathematics | 13 | 7 | 65% |
| Science | 15 | 5 | 75% |
| Turkish History and Reforms | 7 | 3 | 70% |
| English | 6 | 4 | 60% |
| Religious Studies and Ethics | 6 | 4 | 60% |

The fixture includes a complete AI feedback payload with **27 weak topics**, each with a detailed 1-2 sentence study guide.

A 4-second artificial delay keeps the loading animation visible so the demo feels real.

**Production usage**: set `DEMO_MODE=0` in `.env` and provide `GEMINI_API_KEY=...` to run the live pipeline.

---

## Testing

```bash
pytest tests/
```

24 tests cover:
- **Forms** — file extension / content type / size validation
- **URLs** — auth-protected route resolution
- **Views** — upload happy path, history pagination, detail rendering

---

## Team

**Course**: YMH210/220 — Python (2025-2026)

| Member | Main Responsibility Area |
|---|---|
| **Mehlika Türktan** | PDF & Data Core (core) |
| **Nisa Apaydın** | Django Views & Integration (backend orchestrator) |
| **Güler Şenel** | Models, Authentication & Admin |
| **Sema İnce** | Frontend & Templates (UI/UX) |
| **İdil Kinem Karataş** | Analysis, Prediction & Academic Report |

Branch history is preserved on the [GitHub repo](https://github.com/mehlii/Exam-Analyzer-Project) — see `origin/guler`, `origin/sema/frontend-templates`, `origin/mehlika-core`, `origin/idil-kinem-analiz`, `origin/nisa/views-and-pipeline` for individual contributions.

---

## License

Academic project — built for educational purposes as part of YMH210/220.

---

<sub>Built with Django · Gemini AI · scikit-learn · Bootstrap 5 · Chart.js</sub>
