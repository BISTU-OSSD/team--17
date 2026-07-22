import pytest
from unittest.mock import patch, MagicMock
from src.analyzer import analyze_github_project

def test_analyze_github_project_with_valid_input():
    valid_input = """
项目名称: test-project
GitHub地址: https://github.com/test/repo
Star数: 1000
Fork数: 100
主要语言: Python
许可证: MIT

README内容:
这是一个测试项目，用于验证分析模块的功能。

最近Issue数量: 10
最近PR数量: 5
"""
    # 模拟LLM返回的JSON结果
    mock_llm_response = """
{
    "project_name": "test-project",
    "scores": {
        "code_quality": {"score": 8.5, "detail": "Good code quality"},
        "community_activity": {"score": 7.0, "detail": "Active community"},
        "update_frequency": {"score": 9.0, "detail": "Regular updates"},
        "documentation": {"score": 6.5, "detail": "Adequate docs"},
        "security": {"score": 8.0, "detail": "Secure"},
        "community_impact": {"score": 9.5, "detail": "High impact"}
    },
    "summary": "Overall good project"
}
"""
    
    with patch('src.analyzer.stream_chat', return_value=mock_llm_response):
        result = analyze_github_project(valid_input)
    
    # 验证返回结构
    assert "status" in result
    assert "analysis_id" in result
    assert "repo_url" in result
    assert "scores" in result
    assert "total_score" in result
    assert "summary" in result
    assert "timestamp" in result
    
    # 验证scores结构
    required_scores = ["code_quality", "community_activity", "update_frequency", 
                      "documentation", "security", "community_impact"]
    for score_name in required_scores:
        assert score_name in result["scores"]
        assert "score" in result["scores"][score_name]
        assert "detail" in result["scores"][score_name]
    
    # 验证具体值
    assert result["status"] == "success"
    assert result["repo_url"] == "https://github.com/test/repo"
    assert result["total_score"] == 8.1  # (8.5+7.0+9.0+6.5+8.0+9.5)/6 = 8.1
    assert result["summary"] == "Overall good project"