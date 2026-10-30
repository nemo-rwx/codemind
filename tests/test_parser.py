from pathlib import Path

import pytest

from codemind.parser.service import CodeParser


def test_parse_python_file(tmp_path: Path):
    source = """
import os

class UserService:
    def find_user(self, user_id):
        return os.path.exists(user_id)

def greet(name):
    print(name)
"""

    file_path = tmp_path / "example.py"
    file_path.write_text(source, encoding="utf-8")

    parser = CodeParser()
    result = parser.parse_file(file_path)

    assert result.language == "Python"

    symbol_names = [symbol.name for symbol in result.symbols]

    assert "UserService" in symbol_names
    assert "find_user" in symbol_names
    assert "greet" in symbol_names

    assert len(result.imports) == 1
    assert any(call.name == "os.path.exists" for call in result.calls)


def test_parse_java_file(tmp_path: Path):
    source = """
import java.util.List;

public class UserService {
    public void findUser(String id) {
        repository.findById(id);
    }
}
"""

    file_path = tmp_path / "UserService.java"
    file_path.write_text(source, encoding="utf-8")

    parser = CodeParser()
    result = parser.parse_file(file_path)

    assert result.language == "Java"

    symbol_names = [symbol.name for symbol in result.symbols]

    assert "UserService" in symbol_names
    assert "findUser" in symbol_names

    assert len(result.imports) == 1
    assert any(call.name == "findById" for call in result.calls)


def test_unsupported_file_extension(tmp_path: Path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Hello", encoding="utf-8")

    parser = CodeParser()

    with pytest.raises(ValueError):
        parser.parse_file(file_path)
