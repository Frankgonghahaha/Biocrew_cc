#!/usr/bin/env python3
"""
测试CarveMe修复效果的脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.tools.design.carveme import CarvemeTool

def test_carveme_tool():
    """测试Carveme工具"""
    print("开始测试CarveMe工具...")
    
    # 初始化Carveme工具
    carveme_tool = CarvemeTool()
    
    # 创建测试输入目录
    test_input_dir = project_root / "data" / "test"
    test_input_dir.mkdir(exist_ok=True)
    
    print(f"使用测试输入目录: {test_input_dir}")
    
    # 设置输出目录
    output_dir = project_root / "outputs" / "metabolic_models"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"输出目录: {output_dir}")
    
    # 运行CarveMe工具
    result = carveme_tool._run(
        input_path=str(test_input_dir),
        output_path=str(output_dir),
        threads=1,
        overwrite=True
    )
    
    print(f"CarveMe工具执行结果: {result}")
    
    # 检查输出文件
    if result.get("status") == "success":
        data = result.get("data", {})
        model_files = data.get("output_files", [])
        print(f"生成的模型文件: {model_files}")
        
        # 验证模型文件
        for model_file in model_files:
            if os.path.exists(model_file):
                print(f"模型文件存在: {model_file}")
                # 检查文件大小
                file_size = os.path.getsize(model_file)
                print(f"文件大小: {file_size} 字节")
                
                # 读取文件内容检查
                with open(model_file, 'r') as f:
                    content = f.read()
                    print(f"文件内容长度: {len(content)} 字符")
                    if "<model" in content and "</model>" in content:
                        print("模型文件结构完整")
                    else:
                        print("模型文件结构不完整")
            else:
                print(f"模型文件不存在: {model_file}")
    else:
        print(f"CarveMe工具执行失败: {result.get('message', '未知错误')}")
        
        # 检查输出目录中是否有任何文件
        output_files = list(output_dir.glob("*.xml"))
        if output_files:
            print(f"但在输出目录中找到了 {len(output_files)} 个文件:")
            for f in output_files:
                print(f"  - {f}")

if __name__ == "__main__":
    test_carveme_tool()