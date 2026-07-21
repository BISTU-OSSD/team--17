import pytest
import tempfile
import os
from src.file_handler import read_input_file, write_output_file

def test_read_input_file():
    # 创建临时文件，确保使用UTF-8编码
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("项目名称: test-project\nGitHub地址: https://github.com/test/repo")
        temp_path = f.name
    
    try:
        content = read_input_file(temp_path)
        assert "项目名称: test-project" in content
        assert "GitHub地址: https://github.com/test/repo" in content
    finally:
        os.unlink(temp_path)

def test_write_output_file():
    test_data = {
        "status": "success",
        "analysis_id": "test-123",
        "repo_url": "https://github.com/test/repo",
        "scores": {
            "code_quality": {"score": 8.5, "detail": "Good"}
        },
        "total_score": 8.5,
        "summary": "Good project",
        "timestamp": "2026-07-21T10:00:00Z"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        result = write_output_file(test_data, temp_path)
        assert result == True
        
        # 验证文件内容
        with open(temp_path, 'r', encoding='utf-8') as f:
            import json
            saved_data = json.load(f)
            assert saved_data["status"] == "success"
            assert saved_data["analysis_id"] == "test-123"
    finally:
        os.unlink(temp_path)

def test_read_nonexistent_file():
    result = read_input_file("nonexistent.txt")
    assert result is None

def test_write_to_invalid_path():
    test_data = {"status": "success"}
    # 在Windows上，这个路径可能可以创建，所以跳过这个测试
    # 或者使用一个真正无效的路径
    result = write_output_file(test_data, "Z:\\invalid\\path\\file.json")
    assert result == False