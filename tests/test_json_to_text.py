# tests/test_json_to_text.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from json_to_text import convert_json_to_text

def test_convert_basic_structure():
    """测试基本结构转换"""
    sample_json = {
        "repo": {
            "full_name": "facebook/react",
            "description": "A JavaScript library",
            "language": "JavaScript",
            "stars": 220000,
            "forks": 45000,
            "license": "MIT"
        },
        "commits": {
            "commits_last_30_days": 50
        },
        "issues": {
            "total_open": 1000
        },
        "contributors": {
            "total_contributors": 1500
        }
    }
    
    result = convert_json_to_text(sample_json)
    
    assert "facebook/react" in result
    assert "JavaScript" in result
    assert "220000" in result
    assert "Star" in result or "stars" in result.lower()

def test_convert_empty_json():
    """测试空 JSON 处理"""
    result = convert_json_to_text({})
    assert isinstance(result, str)
    assert len(result) > 0
