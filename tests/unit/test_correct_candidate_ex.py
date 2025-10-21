#!/usr/bin/env python3
"""
测试使用正确的候选EX来解决ID不匹配问题
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入必要的库
try:
    from micom import Community
    from cobra.io import read_sbml_model
    import pandas as pd
    print("成功导入必要的库")
except ImportError as e:
    print(f"无法导入必要的库: {e}")
    sys.exit(1)

def test_with_correct_candidate_ex():
    """使用正确的候选EX测试"""
    print("开始测试使用正确的候选EX...")
    
    # 读取一个模型文件
    model_path = str(project_root / "outputs" / "metabolic_models" / "GCF_000014565_1_protein.xml")
    print(f"读取模型文件: {model_path}")
    
    try:
        model = read_sbml_model(model_path)
        print(f"成功读取模型，反应数: {len(model.reactions)}, 代谢物数: {len(model.metabolites)}")
        
        # 查看模型中的交换反应
        exchange_reactions = [r for r in model.reactions if r.id.startswith('EX')]
        print(f"找到 {len(exchange_reactions)} 个交换反应:")
        for rxn in exchange_reactions:
            print(f"  {rxn.id}: {rxn.name}")
        
        # 创建社区
        print("\n创建社区...")
        tax = pd.DataFrame({
            "id": ["test_model"],
            "file": [model_path],
            "abundance": [1.0],
            "biomass": [None],
        }).set_index("id", drop=False)
        
        community = Community(tax, name="TEST_COMMUNITY")
        print(f"成功创建社区")
        
        # 尝试使用MICOM计算完整培养基
        print("\n尝试使用MICOM计算完整培养基...")
        try:
            from micom.media import complete_medium as single_complete
            
            # 使用模型中实际存在的交换反应ID
            candidate_ex = pd.Series({
                "EX_glc__D_e": 10.0,
                "EX_ac_e": 5.0,
            })
            
            print(f"候选EX: {candidate_ex}")
            
            # 尝试计算完整培养基
            fixed = single_complete(
                model=community,
                medium=candidate_ex,
                growth=0.2,
                min_growth=0.05,
                max_import=10.0,
            )
            
            print(f"成功计算完整培养基: {fixed}")
            
        except Exception as e:
            print(f"使用MICOM计算完整培养基时出错: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"读取模型或创建社区时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_correct_candidate_ex()