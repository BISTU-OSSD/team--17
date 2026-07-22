import json
import uuid
from datetime import datetime
from typing import Dict, Any
import requests
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llama_chat import chat, stream_chat, SYSTEM_PROMPT, SERVER_URL, MODEL_PATH

def analyze_github_project(text_content: str) -> Dict[str, Any]:
    """
    分析GitHub项目，返回标准化JSON结果
    
    Args:
        text_content: 上游爬取的纯文本内容
        
    Returns:
        标准化的分析结果字典
    """
    try:
        # 调用LLM分析（流式输出）
        prompt = SYSTEM_PROMPT + "\n" + text_content
        raw_result = stream_chat(prompt, "请评估以上GitHub项目")
        
        # 清理可能的thinking标签和markdown代码块
        cleaned_result = raw_result
        
        # 移除 ```json ... ``` 包裹
        if "```json" in cleaned_result:
            start = cleaned_result.find("```json") + 7
            end = cleaned_result.find("```", start)
            if end != -1:
                cleaned_result = cleaned_result[start:end].strip()
        elif "```" in cleaned_result:
            start = cleaned_result.find("```") + 3
            end = cleaned_result.find("```", start)
            if end != -1:
                cleaned_result = cleaned_result[start:end].strip()
        
        # 移除可能的thinking内容（在<reasoning>标签之间）
        if "<reasoning>" in cleaned_result and "</reasoning>" in cleaned_result:
            start = cleaned_result.find("<reasoning>") + 11
            end = cleaned_result.find("</reasoning>")
            if end != -1:
                cleaned_result = cleaned_result[:start] + cleaned_result[end+12:]
        
        # 解析JSON结果
        try:
            analysis_result = json.loads(cleaned_result)
        except json.JSONDecodeError:
            # 返回完整的失败结构，保证链路完整
            repo_url = ""
            for line in text_content.split("\n"):
                if "GitHub地址:" in line:
                    repo_url = line.split("GitHub地址:")[1].strip()
                    break
            return {
                "status": "failed",
                "analysis_id": str(uuid.uuid4()),
                "repo_url": repo_url,
                "scores": {},
                "total_score": 0.0,
                "summary": "分析失败：模型未返回有效JSON",
                "timestamp": datetime.now().isoformat()
            }
        
        # 提取项目名称（从输入文本中）
        repo_url = ""
        for line in text_content.split("\n"):
            if "GitHub地址:" in line:
                repo_url = line.split("GitHub地址:")[1].strip()
                break
        
        # 构建标准化输出
        standardized_result = {
            "status": "success",
            "analysis_id": str(uuid.uuid4()),
            "repo_url": repo_url,
            "scores": {},
            "total_score": 0.0,
            "summary": "",
            "timestamp": datetime.now().isoformat()
        }
        
        # 直接使用英文键名
        total_score = 0.0
        score_count = 0
        
        for en_name in ["code_quality", "community_activity", "update_frequency", 
                       "documentation", "security", "community_impact"]:
            if en_name in analysis_result.get("scores", {}):
                score_data = analysis_result["scores"][en_name]
                standardized_result["scores"][en_name] = {
                    "score": score_data.get("score", 0),
                    "detail": score_data.get("detail", "")
                }
                total_score += score_data.get("score", 0)
                score_count += 1
        
        # 计算平均分
        if score_count > 0:
            standardized_result["total_score"] = round(total_score / score_count, 1)
        
        # 提取总结建议
        standardized_result["summary"] = analysis_result.get("summary", "")
        
        return standardized_result
        
    except Exception as e:
        return {
            "status": "error",
            "error_type": "ANALYSIS_ERROR",
            "message": str(e)
        }