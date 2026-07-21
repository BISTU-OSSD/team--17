import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from analyze import main

def test_main_with_valid_input():
    # 创建临时输入文件
    input_content = """
项目名称: test-project
GitHub地址: https://github.com/test/repo
Star数: 1000
Fork数: 100
主要语言: Python
许可证: MIT

README内容:
这是一个测试项目。

最近Issue数量: 10
最近PR数量: 5
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(input_content)
        input_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = f.name
    
    try:
        # 模拟分析函数
        mock_result = {
            "status": "success",
            "analysis_id": "test-123",
            "repo_url": "https://github.com/test/repo",
            "scores": {
                "code_quality": {"score": 8.5, "detail": "Good code"},
                "community_activity": {"score": 7.0, "detail": "Active"},
                "update_frequency": {"score": 9.0, "detail": "Regular"},
                "documentation": {"score": 6.5, "detail": "Adequate"},
                "security": {"score": 8.0, "detail": "Secure"},
                "community_impact": {"score": 9.5, "detail": "High impact"}
            },
            "total_score": 8.1,
            "summary": "Overall good project",
            "timestamp": "2026-07-21T10:00:00Z"
        }
        
        with patch('analyze.analyze_github_project', return_value=mock_result):
            # 运行主函数
            with patch('sys.argv', ['analyze.py', input_path, output_path]):
                main()
            
            # 验证输出文件
            assert os.path.exists(output_path)
            with open(output_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
                assert result["status"] == "success"
                assert result["repo_url"] == "https://github.com/test/repo"
    finally:
        os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)