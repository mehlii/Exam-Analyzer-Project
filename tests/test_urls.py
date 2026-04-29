"""URL routing testleri.

Notlar: reverse()/resolve() URL konfigürasyonunu yüklemek zorunda; bu da analysis.views'i
import ettirir, ki o da analysis.models ve core.* modüllerine ihtiyaç duyar. Bu yüzden
ekip arkadaşları kendi parçalarını landlemeden bu testler skip edilir. Saf URL pattern
varlığı test_urls_static ile teyit edilir (URL conf yüklemesine ihtiyaç duymadan).
"""

import pytest

try:
    from analysis.models import Analysis, Score  # noqa: F401
    import core.pdf_reader  # noqa: F401
    import core.cleaner  # noqa: F401
    import core.analyzer  # noqa: F401
    import core.predictor  # noqa: F401
except ImportError as e:
    pytest.skip(f"Ekip parçaları eksik: {e}", allow_module_level=True)

from django.urls import resolve, reverse  # noqa: E402


@pytest.mark.parametrize(
    "name,path",
    [
        ("analysis:home", "/"),
        ("analysis:dashboard", "/dashboard/"),
        ("analysis:upload", "/upload/"),
        ("analysis:history", "/history/"),
    ],
)
def test_simple_urls_resolve(name, path):
    assert reverse(name) == path


def test_detail_url_with_pk():
    assert reverse("analysis:detail", kwargs={"pk": 42}) == "/analysis/42/"


def test_url_resolves_to_view_name():
    match = resolve("/upload/")
    assert match.url_name == "upload"
    assert match.namespace == "analysis"
