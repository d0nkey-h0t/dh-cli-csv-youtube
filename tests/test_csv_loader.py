# tests/test_csv_loader.py
import pytest
from pathlib import Path

from youtube_reports.csv_loader import read_rows, load_rows


class TestReadRows:
    def test_single_file_valid_csv(self, tmp_path: Path):
        # Создаём временный CSV
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,views\nVideo 1,1000\nVideo 2,2500\n", encoding="utf-8")

        rows = list(read_rows(csv_file))
        assert len(rows) == 2
        assert rows[0] == {"name": "Video 1", "views": "1000"}
        assert rows[1] == {"name": "Video 2", "views": "2500"}

    def test_multiple_files(self, tmp_path: Path):
        f1 = tmp_path / "a.csv"
        f2 = tmp_path / "b.csv"
        f1.write_text("title,views\nA,100\n", encoding="utf-8")
        f2.write_text("title,views\nB,200\n", encoding="utf-8")

        rows = list(read_rows([f1, f2]))
        assert len(rows) == 2
        assert rows[0]["title"] == "A"
        assert rows[1]["title"] == "B"

    def test_string_path(self, tmp_path: Path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y\n1,2\n", encoding="utf-8")

        rows = list(read_rows(str(csv_file)))
        assert rows == [{"x": "1", "y": "2"}]

    def test_pathlib_path(self, tmp_path: Path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y\n1,2\n", encoding="utf-8")

        rows = list(read_rows(csv_file))  # Передаём Path напрямую
        assert rows == [{"x": "1", "y": "2"}]

    def test_missing_file_skip(self, tmp_path: Path):
        missing = tmp_path / "missing.csv"
        # Не создаём файл

        rows = list(read_rows(missing, skip_missing=True, verbose=False))
        assert rows == []  # Пропущено без ошибки

    def test_missing_file_raise(self, tmp_path: Path):
        missing = tmp_path / "missing.csv"
        with pytest.raises(FileNotFoundError):
            list(read_rows(missing, skip_missing=False, verbose=False))

    def test_directory_given(self, tmp_path: Path):
        # Передаём директорию вместо файла
        with pytest.raises(IsADirectoryError):
            list(read_rows(tmp_path, skip_missing=False, verbose=False))

    def test_empty_csv_no_header(self, tmp_path: Path):
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("", encoding="utf-8")

        with pytest.raises(RuntimeError, match="no header"):
            list(read_rows(csv_file, skip_missing=False, verbose=False))

    def test_invalid_encoding(self, tmp_path: Path):
        # Записываем в cp1251, но читаем как utf-8 → ошибка декодирования
        csv_file = tmp_path / "bad.csv"
        csv_file.write_text("name,views\nПривет,100\n", encoding="cp1251")

        with pytest.raises(UnicodeDecodeError):
            list(read_rows(csv_file, skip_missing=False, verbose=False))

    def test_invalid_encoding_skip(self, tmp_path: Path, capsys):
        csv_file = tmp_path / "bad.csv"
        csv_file.write_text("name,views\nПривет,100\n", encoding="cp1251")

        rows = list(read_rows(csv_file, skip_missing=True, verbose=True))
        assert rows == []
        captured = capsys.readouterr()
        assert "Cannot decode CSV as UTF-8" in captured.err

    def test_malformed_csv_with_extra_columns(self, tmp_path: Path):
        # Даже если строк больше, чем заголовков — DictReader пропускает лишние
        csv_file = tmp_path / "extra.csv"
        csv_file.write_text("name\nAlice,25\nBob,30\n", encoding="utf-8")

        rows = list(read_rows(csv_file))
        assert rows == [{"name": "Alice"}, {"name": "Bob"}]  # остальные поля игнорируются

    def test_blank_lines_ignored(self, tmp_path: Path):
        csv_file = tmp_path / "blank.csv"
        csv_file.write_text("name\nAlice\n\nBob\n", encoding="utf-8")

        rows = list(read_rows(csv_file))
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["name"] == "Bob"


class TestLoadRows:
    def test_load_rows_simple(self, tmp_path: Path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x\n1\n2\n", encoding="utf-8")

        rows = load_rows(csv_file)
        assert rows == [{"x": "1"}, {"x": "2"}]

    def test_load_rows_with_skip(self, tmp_path: Path):
        existing = tmp_path / "ok.csv"
        missing = tmp_path / "nope.csv"
        existing.write_text("x\n1\n", encoding="utf-8")

        rows = load_rows([existing, missing], skip_missing=True, verbose=False)
        assert len(rows) == 1
        assert rows[0]["x"] == "1"