from codemind.scanner.service import RepositoryScanner


def test_scanner_detects_files(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "Main.java").write_text(
        "public class Main {}", encoding="utf-8"
    )
    (tmp_path / "app.py").write_text("print('Hello')", encoding="utf-8")

    result = RepositoryScanner().scan(tmp_path)

    assert result.total_files == 2
    assert result.language_counts["Java"] == 1
    assert result.language_counts["Python"] == 1


def test_scanner_ignores_venv(tmp_path):
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "ignored.py").write_text("print('ignored')", encoding="utf-8")
    (tmp_path / "main.py").write_text("print('included')", encoding="utf-8")

    result = RepositoryScanner().scan(tmp_path)

    assert result.total_files == 1


def test_scanner_rejects_missing_directory(tmp_path):
    missing = tmp_path / "does-not-exist"

    try:
        RepositoryScanner().scan(missing)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError")
