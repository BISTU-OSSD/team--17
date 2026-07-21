import json
import pytest
from src.file_handler import read_input_file, write_output_file


def test_read_input_file(tmp_path):
    # 使用 pytest 提供的 tmp_path fixture，测试结束后会自动清理临时文件
    test_file = tmp_path / "input.txt"
    test_file.write_text(
        "项目名称: test-project\nGitHub地址: https://github.com/test/repo",
        encoding="utf-8",
    )

    content = read_input_file(str(test_file))
    assert "项目名称: test-project" in content
    assert "GitHub地址: https://github.com/test/repo" in content


def test_write_output_file(tmp_path):
    test_data = {
        "status": "success",
        "analysis_id": "test-123",
        "repo_url": "https://github.com/test/repo",
        "scores": {"code_quality": {"score": 8.5, "detail": "Good"}},
        "total_score": 8.5,
        "summary": "Good project",
        "timestamp": "2026-07-21T10:00:00Z",
    }

    output_file = tmp_path / "output.json"
    result = write_output_file(test_data, str(output_file))

    assert result is True

    # 验证写入内容
    saved_data = json.loads(output_file.read_text(encoding="utf-8"))
    assert saved_data["status"] == "success"
    assert saved_data["analysis_id"] == "test-123"


def test_read_nonexistent_file():
    result = read_input_file("nonexistent.txt")
    assert result is None


def test_write_to_invalid_path(tmp_path):
    test_data = {"status": "success"}

    # 1. 在不存在的子目录下尝试写入文件（如果不自动创建文件夹，它会抛出 FileNotFoundError 并返回 False）
    # 2. 或者在路径中传入 \0 (Null Byte)，这在 Linux/macOS/Windows 下都会触发系统的 Invalid Path 异常
    invalid_path = "\0/invalid_path/file.json"

    result = write_output_file(test_data, invalid_path)
    assert result is False