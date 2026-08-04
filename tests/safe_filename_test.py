import pytest


def test_safe_filename_strips_crlf_and_path_segments():
    from controllers.ressource_controller import _safe_filename

    value = "..\\..\\evil\r\nX-Injected: 1.pdf"
    result = _safe_filename(value)

    assert "\r" not in result
    assert "\n" not in result
    assert "/" not in result
    assert "\\" not in result
    assert "Injected" in result
    assert result.endswith(".pdf")


@pytest.mark.parametrize(
    "value",
    [
        "  \"report\".pdf  ",
        "'report'.pdf",
        "“report”.pdf",
        "report;name.pdf",
    ],
)
def test_safe_filename_removes_problematic_punctuation(value: str):
    from controllers.ressource_controller import _safe_filename

    result = _safe_filename(value)
    assert result.endswith(".pdf")
    assert "\"" not in result
    assert "'" not in result
    assert ";" not in result


def test_safe_filename_falls_back_to_download():
    from controllers.ressource_controller import _safe_filename

    assert _safe_filename("") == "download"
    assert _safe_filename("   ") == "download"
    assert _safe_filename("\r\n") == "download"
    assert _safe_filename("...") == "download"
