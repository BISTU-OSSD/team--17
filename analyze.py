import sys
import os
import argparse

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import analyze_github_project
from file_handler import read_input_file, write_output_file
from validators import validate_analysis_result

def main():
    parser = argparse.ArgumentParser(description='GitHub项目分析工具')
    parser.add_argument('input_file', help='上游输入文件路径（支持 .txt 或 .json）')
    parser.add_argument('output_file', help='输出JSON文件路径')
    parser.add_argument('--input-format', choices=['auto', 'txt', 'json'],
                       default='auto', help='输入格式（默认自动检测）')
    
    args = parser.parse_args()
    
    print(f"开始分析项目...")
    print(f"输入文件: {args.input_file}")
    print(f"输出文件: {args.output_file}")
    print(f"输入格式: {args.input_format}")
    
    # 读取输入文件
    text_content = read_input_file(args.input_file)
    if text_content is None:
        print("错误: 无法读取输入文件")
        sys.exit(1)
    
    # 分析项目
    print("正在调用LLM进行分析...")
    result = analyze_github_project(text_content)
    
    # 验证结果
    if result.get("status") == "error":
        print(f"分析失败: {result.get('message', '未知错误')}")
        # 写入错误结果
        write_output_file(result, args.output_file)
        sys.exit(1)
    
    # 处理失败但结构完整的响应
    if result.get("status") == "failed":
        print(f"警告: {result.get('summary', '分析失败')}")
    
    # 验证输出格式
    if not validate_analysis_result(result):
        print("警告: 输出格式不符合标准，但仍然保存")
    
    # 写入输出文件
    if write_output_file(result, args.output_file):
        print("分析完成!")
        print(f"结果已保存到: {args.output_file}")
        print(f"项目总分: {result.get('total_score', 'N/A')}")
    else:
        print("错误: 无法写入输出文件")
        sys.exit(1)

if __name__ == "__main__":
    main()