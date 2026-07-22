# src/json_to_text.py
"""JSON 结构化数据到文本格式的转换器"""

from typing import Dict, Any


def convert_json_to_text(data: Dict[str, Any]) -> str:
    """
    将 RepoReport JSON 转换为纯文本格式
    
    Args:
        data: RepoReport 结构化数据字典
        
    Returns:
        格式化的纯文本字符串
    """
    lines = []
    
    # 仓库基本信息
    repo = data.get("repo", {})
    if repo:
        lines.append(f"项目名称: {repo.get('name', '未知')}")
        lines.append(f"GitHub地址: https://github.com/{repo.get('full_name', '')}")
        lines.append(f"项目描述: {repo.get('description', '无')}")
        lines.append(f"主要语言: {repo.get('language', '未知')}")
        lines.append(f"Star数: {repo.get('stars', 0)}")
        lines.append(f"Fork数: {repo.get('forks', 0)}")
        lines.append(f"许可证: {repo.get('license', '未知')}")
        lines.append(f"Open Issues: {repo.get('open_issues_count', 0)}")
        lines.append("")
    
    # 语言分布
    languages = data.get("languages", {})
    if languages and languages.get("languages"):
        lines.append("语言分布:")
        for lang in languages["languages"][:5]:  # 只显示前5种
            lines.append(f"  - {lang.get('language')}: {lang.get('percentage', 0):.1f}%")
        lines.append("")
    
    # Commit 活跃度
    commits = data.get("commits", {})
    if commits:
        lines.append("提交活跃度:")
        lines.append(f"  近30天提交: {commits.get('commits_last_30_days', 0)}")
        lines.append(f"  近90天提交: {commits.get('commits_last_90_days', 0)}")
        lines.append(f"  每周平均: {commits.get('commit_frequency_per_week', 0)}")
        lines.append(f"  最近提交: {commits.get('last_commit_date', '未知')}")
        lines.append("")
    
    # Issue 统计
    issues = data.get("issues", {})
    if issues:
        lines.append("Issue 统计:")
        lines.append(f"  开放Issue数: {issues.get('total_open', 0)}")
        lines.append(f"  关闭率: {issues.get('close_rate', 0) * 100:.1f}%")
        avg_close = issues.get('avg_close_time_hours')
        if avg_close:
            lines.append(f"  平均关闭时长: {avg_close:.1f}小时")
        lines.append("")
    
    # PR 统计
    pulls = data.get("pulls", {})
    if pulls:
        lines.append("PR 统计:")
        lines.append(f"  已合并PR: {pulls.get('total_merged', 0)}")
        lines.append(f"  合并率: {pulls.get('merge_rate', 0) * 100:.1f}%")
        avg_merge = pulls.get('avg_merge_time_hours')
        if avg_merge:
            lines.append(f"  平均合并时长: {avg_merge:.1f}小时")
        lines.append("")
    
    # 贡献者画像
    contributors = data.get("contributors", {})
    if contributors:
        lines.append("贡献者信息:")
        lines.append(f"  总贡献者数: {contributors.get('total_contributors', 0)}")
        lines.append(f"  近30天活跃: {contributors.get('active_30d_contributors', 0)}")
        lines.append(f"  Bus Factor: {contributors.get('bus_factor', 0)}")
        lines.append("")
    
    # 文档质量
    docs = data.get("docs", {})
    if docs:
        lines.append("文档质量:")
        lines.append(f"  README: {'有' if docs.get('has_readme') else '无'}")
        lines.append(f"  CONTRIBUTING: {'有' if docs.get('has_contributing') else '无'}")
        lines.append(f"  LICENSE: {'有' if docs.get('has_license') else '无'}")
        lines.append(f"  CHANGELOG: {'有' if docs.get('has_changelog') else '无'}")
        lines.append("")
    
    # 发布信息
    releases = data.get("releases", {})
    if releases:
        lines.append("版本发布:")
        lines.append(f"  总发布数: {releases.get('total_releases', 0)}")
        lines.append(f"  最新版本: {releases.get('latest_release_tag', '未知')}")
        lines.append(f"  最新发布日期: {releases.get('latest_release_date', '未知')}")
        lines.append("")
    
    result = "\n".join(lines)
    
    # 如果没有数据，返回默认提示
    if not result.strip():
        return "无有效数据"
    
    return result
