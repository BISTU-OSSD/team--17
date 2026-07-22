import json
import os
import sys
from typing import Optional

# 添加src目录到路径
sys.path.append(os.path.dirname(__file__))
from json_to_text import convert_json_to_text

def read_input_file(file_path: str) -> Optional[str]:
    """
    读取上游输入文件，自动检测格式
    
    Args:
        file_path: 输入文件路径（支持 .txt 和 .json）
        
    Returns:
        文本内容，如果文件不存在则返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检测是否为 JSON 文件
        if file_path.lower().endswith('.json'):
            try:
                json_data = json.loads(content)
                # 如果是 RepoReport 格式，转换为文本
                if isinstance(json_data, dict) and ('repo' in json_data or 'languages' in json_data):
                    return convert_json_to_text(json_data)
                # 否则作为普通文本返回
                return content
            except json.JSONDecodeError:
                # JSON 解析失败，作为普通文本返回
                return content
        
        # 非 JSON 文件，直接返回文本
        return content
        
    except FileNotFoundError:
        print(f"错误: 文件不存在 {file_path}")
        return None
    except Exception as e:
        print(f"错误: 读取文件失败 {e}")
        return None

def write_output_file(data: dict, output_path: str) -> bool:
    """
    写入JSON输出文件
    
    Args:
        data: 要写入的数据
        output_path: 输出文件路径
        
    Returns:
        是否成功写入
    """
    try:
        # 确保目录存在（处理文件名没有目录的情况）
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"成功写入文件: {output_path}")
        return True
    except Exception as e:
        print(f"错误: 写入文件失败 {e}")
        return False
