#!/usr/bin/env python3
"""
测试DLkcat工具的集成效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dlkcat_tool import DLkcatTool

def test_dlkcat_tool():
    """测试DLkcat工具"""
    # 创建工具实例
    tool = DLkcatTool()
    
    # 测试参数
    test_params = {
        "script_path": "/home/axlhuang/Agent-tool/DesignAgent/Tool_DLkcat/run_DLkcat.py",
        "file_path": "/home/axlhuang/BioCrew/tools/microbial_agent_design/dlkcat_tool/test_data.xlsx",
        "output_path": "/tmp/test_output.xlsx"
    }
    
    # 检查测试文件是否存在
    if not os.path.exists(test_params["script_path"]):
        print(f"预测脚本不存在: {test_params['script_path']}")
        return
    
    # 创建测试数据
    import pandas as pd
    test_data = {
        "Enzyme": ["patE", "pehA"],
        "Sequence": [
            "MSALTAAAEEYQRLRTEFREKGLGGRIGFGVRPAVVVVDLITGFTDRRSPLAGDLDTQIDATKILLALARKAQVPIIFSTVAYDAELQEAGAWIGKIPSNKYLVEGSQWVEIDERLEQQPGETTLVKKYASCFFGTDLAARLISRRIDTVIIVGCTTSGCVRATAVDACSYGFHTIVVEDAVGDRAALPHTASLFDIDAKYGDVVGLDEASAYLESVPSSS",
            "MEIVLVHGGWVGGWVWDGVADELRRMGHEVIAPTLRGLEDGDVDRSGVTMSMMARDLIDQVRELTQLDIVLVGHSGGGPLIQLVAEAMPERIGRVVFVDAWVLRDGETINDVLPDPLVAATKALASQSDDNTIVMPPELWAASMQDMSPFEQQQLAALEPRLVPSPAGWSDEPIRLDRFWASSIPSSYVFLAQDQAVPAEIYQAAAGRLDSPRTIEIDGSHLVMLTHPERLARALDAVIA"
        ],
        "substrate_name": ["Dibutyl Phthalate", "Dibutyl Phthalate"],
        "substrate_smiles": ["O=C(C1=CC=CC=C1C(=O)OCCCC)OCCCC", "O=C(C1=CC=CC=C1C(=O)OCCCC)OCCCC"]
    }
    
    # 创建测试Excel文件
    df = pd.DataFrame(test_data)
    df.to_excel(test_params["file_path"], index=False)
    print(f"已创建测试Excel文件: {test_params['file_path']}")
    
    # 运行工具
    print("运行DLkcat工具...")
    result = tool._run(**test_params)
    
    # 输出结果
    print("测试结果:")
    print(f"状态: {result.get('status')}")
    if result.get('status') == 'success':
        data = result.get('data', {})
        print(f"输出文件: {data.get('output_file')}")
        print(f"Kcat值: {data.get('kcat_values')}")
        print(f"行数: {data.get('row_count')}")
    else:
        print(f"错误信息: {result.get('message')}")

if __name__ == "__main__":
    test_dlkcat_tool()