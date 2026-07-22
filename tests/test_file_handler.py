# tests/test_file_handler.py
import sys
import os
import tempfile
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from file_handler import read_input_file

def test_read_txt_file():
    """测试读取纯文本文件"""
    content = "项目名称: test\nGitHub地址: https://github.com/test/repo"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        result = read_input_file(temp_path)
        assert result == content
    finally:
        os.unlink(temp_path)

def test_read_json_file():
    """测试读取 JSON 文件"""
    json_data = {
        "repo": {
            "full_name": "test/repo",
            "name": "repo",
            "stars": 100
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(json_data, f)
        temp_path = f.name
    
    try:
        result = read_input_file(temp_path)
        assert isinstance(result, str)
        assert "test/repo" in result
        assert "100" in result
    finally:
        os.unlink(temp_path)
