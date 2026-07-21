import pytest
from src.validators import validate_analysis_result

def test_valid_analysis_result():
    valid_data = {
        "status": "success",
        "analysis_id": "test-123",
        "repo_url": "https://github.com/test/repo",
        "scores": {
            "code_quality": {"score": 8.5, "detail": "Good code quality"},
            "community_activity": {"score": 7.0, "detail": "Active community"},
            "update_frequency": {"score": 9.0, "detail": "Regular updates"},
            "documentation": {"score": 6.5, "detail": "Adequate docs"},
            "security": {"score": 8.0, "detail": "Secure"},
            "community_impact": {"score": 9.5, "detail": "High impact"}
        },
        "total_score": 8.1,
        "summary": "Overall good project",
        "timestamp": "2026-07-21T10:00:00Z"
    }
    assert validate_analysis_result(valid_data) == True

def test_invalid_missing_status():
    invalid_data = {"repo_url": "https://github.com/test/repo"}
    assert validate_analysis_result(invalid_data) == False

def test_invalid_score_range():
    invalid_data = {
        "status": "success",
        "analysis_id": "test-123",
        "repo_url": "https://github.com/test/repo",
        "scores": {
            "code_quality": {"score": 15.0, "detail": "Out of range"},  # 超过10分
            "community_activity": {"score": 7.0, "detail": "Good"},
            "update_frequency": {"score": 9.0, "detail": "Good"},
            "documentation": {"score": 6.5, "detail": "Good"},
            "security": {"score": 8.0, "detail": "Good"},
            "community_impact": {"score": 9.5, "detail": "Good"}
        },
        "total_score": 8.1,
        "summary": "Good",
        "timestamp": "2026-07-21T10:00:00Z"
    }
    assert validate_analysis_result(invalid_data) == False