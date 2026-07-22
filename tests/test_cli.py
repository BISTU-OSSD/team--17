# tests/test_cli.py
import sys
import os
import subprocess
sys.path.append(os.path.dirname(__file__))

def test_analyze_help():
    """测试分析工具帮助信息"""
    result = subprocess.run(
        [sys.executable, 'analyze.py', '--help'],
        capture_output=True,
        cwd=os.path.join(os.path.dirname(__file__), '..')
    )
    assert result.returncode == 0
    # 检查输出中包含 input_file
    assert b'input_file' in result.stdout
