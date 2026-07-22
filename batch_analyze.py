"""批量分析：支持目录批量分析和单文件分析"""

import os
import sys
import glob
import time
import argparse

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import analyze_github_project
from file_handler import read_input_file, write_output_file
from validators import validate_analysis_result


def analyze_single(input_file, output_file):
    """分析单个文件"""
    # 读取输入
    text_content = read_input_file(input_file)
    if text_content is None:
        return False, "无法读取输入文件"
    
    # 分析
    result = analyze_github_project(text_content)
    
    # 检查错误
    if result.get("status") == "error":
        return False, result.get("message", "未知错误")
    
    # 验证格式
    if not validate_analysis_result(result):
        pass  # 格式警告已记录到errors.log
    
    # 写入输出
    if write_output_file(result, output_file):
        if result.get("status") == "failed":
            return True, "failed"
        return True, result.get("total_score", "N/A")
    else:
        return False, "写入文件失败"


def batch_analyze(input_path, output_path):
    """批量分析"""
    # 检查输入是文件还是目录
    if os.path.isfile(input_path):
        # 单文件模式
        print(f"单文件模式")
        print(f"输入: {input_path}")
        print(f"输出: {output_path}")
        print("-" * 40)
        
        success, msg = analyze_single(input_file=input_path, output_file=output_path)
        
        if success:
            print(f"✓ 分析完成, 总分: {msg}")
        else:
            print(f"✗ 分析失败: {msg}")
        
        return 1 if success else 0
    
    elif os.path.isdir(input_path):
        # 目录模式
        # 获取所有txt文件
        txt_files = glob.glob(os.path.join(input_path, "*.txt"))
        
        if not txt_files:
            print(f"错误: 目录 {input_path} 中没有找到 .txt 文件")
            return 0
        
        # 创建输出目录
        os.makedirs(output_path, exist_ok=True)
        
        total = len(txt_files)
        success_count = 0
        fail_count = 0
        errors = []
        
        print(f"批量分析模式")
        print(f"输入目录: {input_path}")
        print(f"输出目录: {output_path}")
        print(f"找到 {total} 个文件")
        print("=" * 40)
        
        start_time = time.time()
        
        for i, txt_file in enumerate(txt_files, 1):
            # 获取文件名（不含路径和扩展名）
            basename = os.path.splitext(os.path.basename(txt_file))[0]
            output_file = os.path.join(output_path, f"{basename}.json")
            
            print(f"[{i}/{total}] {basename}.txt → {basename}.json", end=" ... ")
            
            try:
                success, msg = analyze_single(input_file=txt_file, output_file=output_file)
                
                if success and msg == "failed":
                    fail_count += 1
                    errors.append((basename, "模型未返回有效JSON"))
                elif success:
                    print(f"✓ (总分: {msg})")
                    success_count += 1
                else:
                    fail_count += 1
                    errors.append((basename, msg))
            except Exception as e:
                fail_count += 1
                errors.append((basename, str(e)))
        
        elapsed = time.time() - start_time
        
        # 汇总
        print("=" * 40)
        print(f"完成!")
        print(f"  成功: {success_count}/{total}")
        print(f"  失败: {fail_count}/{total}")
        print(f"  耗时: {elapsed:.1f}秒")
        
        # 记录错误到单独的log文件夹
        if errors:
            log_dir = os.path.join(output_path, "logs")
            os.makedirs(log_dir, exist_ok=True)
            error_log = os.path.join(log_dir, "errors.log")
            with open(error_log, "w", encoding="utf-8") as f:
                for name, error in errors:
                    f.write(f"{name}: {error}\n")
        
        return success_count
    
    else:
        print(f"错误: 路径不存在: {input_path}")
        return 0


def main():
    parser = argparse.ArgumentParser(description='GitHub项目批量分析工具')
    parser.add_argument('input', help='输入文件或目录')
    parser.add_argument('output', help='输出文件或目录')
    
    args = parser.parse_args()
    
    result = batch_analyze(input_path=args.input, output_path=args.output)
    sys.exit(0 if result > 0 else 1)


if __name__ == "__main__":
    main()