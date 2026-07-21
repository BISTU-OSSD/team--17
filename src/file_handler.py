import json
import os
from typing import Optional

def read_input_file(file_path: str) -> Optional[str]:
    """
    读取上游输入文件
    
    Args:
        file_path: 输入文件路径
        
    Returns:
        文件内容，如果文件不存在则返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
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