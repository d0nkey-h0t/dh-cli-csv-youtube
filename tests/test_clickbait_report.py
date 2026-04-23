import pytest

from youtube_reports.reports import get_report
from youtube_reports.reports.clickbait import ClickbaitReport


@pytest.fixture
def sample_rows():
    return [
        {"title": "High CTR low retention", "ctr": "18.2", "retention_rate": "35"},
        {"title": "Very high CTR low retention", "ctr": "25.0", "retention_rate": "22"},
        {"title": "Boring but loyal", "ctr": "9.5", "retention_rate": "82"},
        {"title": "On the CTR boundary", "ctr": "15", "retention_rate": "20"},
        {"title": "On the retention boundary", "ctr": "20", "retention_rate": "40"},
        {"title": "Honest viral", "ctr": "21", "retention_rate": "60"},
        {"title": "Mid CTR mid retention", "ctr": "16.5", "retention_rate": "42"},
        {"title": "Another clickbait", "ctr": "19.0", "retention_rate": "38"},
    ]


def test_only_videos_matching_thresholds_are_included(sample_rows):
    report = ClickbaitReport()
    titles = [row[0] for row in report.build(sample_rows)]
    assert set(titles) == {
        "High CTR low retention",
        "Very high CTR low retention",
        "Another clickbait",
    }


def test_results_are_sorted_by_ctr_descending(sample_rows):
    report = ClickbaitReport()
    rows = report.build(sample_rows)
    ctrs = [row[1] for row in rows]
    assert ctrs == sorted(ctrs, reverse=True)


def test_report_columns(sample_rows):
    report = ClickbaitReport()
    assert report.headers == ("title", "ctr", "retention_rate")
    rows = report.build(sample_rows)
    for row in rows:
        assert len(row) == 3


def test_strict_inequalities():
    report = ClickbaitReport()
    rows = [
        {"title": "ctr exactly 15", "ctr": "15", "retention_rate": "10"},
        {"title": "retention exactly 40", "ctr": "20", "retention_rate": "40"},
        {"title": "qualifies", "ctr": "15.01", "retention_rate": "39.99"},
    ]
    titles = [r[0] for r in report.build(rows)]
    assert titles == ["qualifies"]


def test_skips_rows_with_invalid_or_missing_values():
    report = ClickbaitReport()
    rows = [
        {"title": "missing ctr", "ctr": "", "retention_rate": "10"},
        {"title": "bad ctr", "ctr": "abc", "retention_rate": "10"},
        {"title": "", "ctr": "20", "retention_rate": "10"},
        {"title": "ok", "ctr": "20", "retention_rate": "10"},
    ]
    titles = [r[0] for r in report.build(rows)]
    assert titles == ["ok"]


def test_report_is_registered():
    assert isinstance(get_report("clickbait"), ClickbaitReport)
