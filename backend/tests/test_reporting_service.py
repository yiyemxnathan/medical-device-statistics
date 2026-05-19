from app.services.reporting import build_report_html


def test_build_report_html_includes_versions_and_result():
    html = build_report_html(
        title="Sampling Plan Report",
        metadata={
            "report_number": "R-001",
            "app_version": "0.1.0",
            "algorithm_version": "sampling-statistics-0.1.0",
            "standard_package": "GB2828-2012-demo",
        },
        sections=[
            {"heading": "Result", "body": "Sample size 80, Ac 2, Re 3"},
        ],
    )

    assert "Sampling Plan Report" in html
    assert "R-001" in html
    assert "sampling-statistics-0.1.0" in html
    assert "Sample size 80" in html


def test_build_report_html_escapes_metadata_and_sections():
    html = build_report_html(
        title="<Report>",
        metadata={"operator": "A&B"},
        sections=[
            {"heading": "Result <unsafe>", "body": "Sample < 80 & Ac > 2"},
        ],
    )

    assert "&lt;Report&gt;" in html
    assert "A&amp;B" in html
    assert "Result &lt;unsafe&gt;" in html
    assert "Sample &lt; 80 &amp; Ac &gt; 2" in html
    assert "<Report>" not in html
    assert "A&B" not in html
