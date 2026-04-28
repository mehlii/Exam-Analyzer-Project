"""View davranış testleri — ekip arkadaşları kendi parçalarını landlemeden çalışmaz.

Bu dosya, `analysis.models` (Güler) ve `core.*` (Mehlika, İdil) modülleri var olduğunda
otomatik olarak aktif olur. O zamana kadar tüm testler skip edilir.
"""

import pytest

# Ekip henüz parçalarını landlemediyse testleri tamamen skip et.
try:
    from analysis.models import Analysis  # noqa: F401
    import core.pdf_reader  # noqa: F401
    import core.cleaner  # noqa: F401
    import core.analyzer  # noqa: F401
    import core.predictor  # noqa: F401
except ImportError as e:
    pytest.skip(f"Ekip parçaları eksik: {e}", allow_module_level=True)

from django.contrib.auth.models import User  # noqa: E402
from django.urls import reverse  # noqa: E402

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(db):
    return User.objects.create_user(username="nisa", password="testpass123")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="other", password="testpass123")


@pytest.fixture
def authed_client(client, user):
    client.force_login(user)
    return client


def test_dashboard_requires_login(client):
    res = client.get(reverse("analysis:dashboard"))
    assert res.status_code == 302
    assert "/accounts/login" in res.url or "login" in res.url.lower()


def test_dashboard_renders_when_logged_in(authed_client):
    res = authed_client.get(reverse("analysis:dashboard"))
    assert res.status_code == 200


def test_upload_get_requires_login(client):
    res = client.get(reverse("analysis:upload"))
    assert res.status_code == 302


def test_upload_post_invalid_file_returns_form(authed_client):
    res = authed_client.post(reverse("analysis:upload"), {"pdf_file": ""})
    assert res.status_code == 200
    assert "form" in res.context


def test_detail_404_for_other_users_analysis(authed_client, other_user):
    foreign = Analysis.objects.create(user=other_user, summary_json={})
    res = authed_client.get(reverse("analysis:detail", kwargs={"pk": foreign.pk}))
    assert res.status_code == 404


def test_history_paginates(authed_client, user):
    for _ in range(11):
        Analysis.objects.create(user=user, summary_json={})
    res = authed_client.get(reverse("analysis:history") + "?page=2")
    assert res.status_code == 200
    page = res.context["page"]
    assert page.number == 2
    assert len(page.object_list) == 1
