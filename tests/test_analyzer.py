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
    "项目名称": "test-project",
    "评分": {
        "代码质量": {"分数": 8.5, "说明": "Good code quality"},
        "社区活跃度": {"分数": 7.0, "说明": "Active community"},
        "更新频率": {"分数": 9.0, "说明": "Regular updates"},
        "文档完整性": {"分数": 6.5, "说明": "Adequate docs"},
        "安全状况": {"分数": 8.0, "说明": "Secure"},
        "社区影响力": {"分数": 9.5, "说明": "High impact"}
    },
    "总结建议": "Overall good project"
}
"""
    
    with patch('src.analyzer.chat', return_value=mock_llm_response):
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