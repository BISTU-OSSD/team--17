from typing import Dict, Any

def validate_analysis_result(data: Dict[str, Any]) -> bool:
    """验证分析结果是否符合标准格式"""
    required_fields = ["status", "analysis_id", "repo_url", "scores", "total_score", "summary", "timestamp"]
    
    # 检查必需字段
    for field in required_fields:
        if field not in data:
            return False
    
    # 验证status
    if data["status"] not in ["success", "failed"]:
        return False
    
    # 验证scores结构（失败时scores可能为空）
    if data["status"] == "success":
        required_scores = ["code_quality", "community_activity", "update_frequency", 
                          "documentation", "security", "community_impact"]
        for score_name in required_scores:
            if score_name not in data["scores"]:
                return False
            score_data = data["scores"][score_name]
            if "score" not in score_data or "detail" not in score_data:
                return False
            # 验证分数范围
            if not (0 <= score_data["score"] <= 10):
                return False
    
    # 验证total_score
    if not (0 <= data["total_score"] <= 10):
        return False
    
    return True