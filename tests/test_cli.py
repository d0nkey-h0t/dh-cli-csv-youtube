from pathlib import Path

import pytest

from youtube_reports.cli import run


SAMPLE_CSV = (
    "title,ctr,retention_rate,views,likes,avg_watch_time\n"
    "Я бросил IT и стал фермером,18.2,35,45200,1240,4.2\n"
    "Как я спал по 4 часа и ничего не понял,22.5,28,128700,3150,3.1\n"
    "Почему сеньоры не носят галстуки,9.5,82,31500,890,8.9\n"
    "Секрет который скрывают тимлиды,25.0,22,254000,8900,2.5\n"
    "Купил джуну макбук и он уволился,19.0,38,87600,2100,4.5\n"
    "Честный обзор на печеньки в офисе,6.0,91,12300,450,10.2\n"
    "Как я задолжал ревьюеру 1000 строк кода,21.0,35,67300,1890,4.0\n"
    "Рефакторинг выходного дня,8.5,76,28900,780,7.8\n"
    "Почему я не использую ChatGPT на собесах,16.5,42,54100,1320,4.8\n"
    "Я переписал всё на Go и пожалел,14.2,68,43800,1150,6.5\n"
)


def test_cli_clickbait_report_prints_expected_titles(tmp_path, capsys):
    f = tmp_path / "videos.csv"
    f.write_text(SAMPLE_CSV, encoding="utf-8")

    exit_code = run(["--files", str(f), "--report", "clickbait"])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "title" in out and "ctr" in out and "retention_rate" in out

    expected_in_order = [
        "Секрет который скрывают тимлиды",
        "Как я спал по 4 часа и ничего не понял",
        "Как я задолжал ревьюеру 1000 строк кода",
        "Купил джуну макбук и он уволился",
        "Я бросил IT и стал фермером",
    ]
    positions = [out.find(t) for t in expected_in_order]
    assert all(p > 0 for p in positions), positions
    assert positions == sorted(positions)

    excluded = [
        "Почему сеньоры не носят галстуки",
        "Честный обзор на печеньки в офисе",
        "Рефакторинг выходного дня",
        "Почему я не использую ChatGPT на собесах",
        "Я переписал всё на Go и пожалел",
    ]
    for title in excluded:
        assert title not in out


def test_cli_combines_multiple_files(tmp_path, capsys):
    f1 = tmp_path / "a.csv"
    f2 = tmp_path / "b.csv"
    f1.write_text("title,ctr,retention_rate\nA,20,30\n", encoding="utf-8")
    f2.write_text("title,ctr,retention_rate\nB,30,10\n", encoding="utf-8")

    run(["--files", str(f1), str(f2), "--report", "clickbait"])
    out = capsys.readouterr().out
    assert "A" in out and "B" in out
    assert out.find("B") < out.find("A")


def test_cli_requires_files_and_report():
    with pytest.raises(SystemExit):
        run([])


def test_cli_rejects_unknown_report(tmp_path):
    f = tmp_path / "v.csv"
    f.write_text("title,ctr,retention_rate\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        run(["--files", str(f), "--report", "no_such_report"])
