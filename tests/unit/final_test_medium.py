#!/usr/bin/env python3
"""
使用正确的候选EX ID测试（使用MICOM转换后的ID）
"""

import sys
import os
from pathlib import Path
import pandas as pd

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入必要的库
try:
    from micom import Community
    from cobra.io import read_sbml_model
    from micom.media import complete_medium as single_complete
    print("成功导入必要的库")
except ImportError as e:
    print(f"无法导入必要的库: {e}")
    sys.exit(1)

def final_test():
    """最终测试"""
    print("开始最终测试...")
    
    # 读取一个模型文件
    model_path = str(project_root / "outputs" / "metabolic_models" / "GCF_000014565_1_protein.xml")
    print(f"读取模型文件: {model_path}")
    
    try:
        model = read_sbml_model(model_path)
        print(f"成功读取模型")
        
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
        
        # 查看社区中的交换反应（这些是实际可用的ID）
        print("\n社区中的交换反应:")
        exchange_ids = []
        for rxn in community.exchanges:
            print(f"  {rxn.id}: {rxn.name}")
            exchange_ids.append(rxn.id)
        
        # 尝试使用MICOM转换后的ID
        print("\n尝试使用MICOM转换后的交换反应ID...")
        try:
            # 使用社区中实际存在的交换反应ID
            candidate_ex = pd.Series({
                "EX_glc__D_m": 10.0,
                "EX_ac_m": 5.0,
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
            
            print(f"✅ 成功计算完整培养基!")
            print(f"结果: {fixed}")
            
        except Exception as e:
            print(f"❌ 使用MICOM计算完整培养基时出错: {e}")
            
            # 如果上面的方法失败，尝试另一种方法
            print("\n尝试另一种方法...")
            try:
                # 直接设置社区的培养基
                medium = pd.Series({rxn.id: 10.0 for rxn in community.exchanges})
                community.medium = medium
                print(f"✅ 成功设置社区培养基: {medium}")
                
                # 尝试优化
                solution = community.optimize()
                print(f"✅ 优化成功，目标值: {solution.objective_value}")
                
            except Exception as e2:
                print(f"❌ 另一种方法也失败: {e2}")
        
    except Exception as e:
        print(f"读取模型或创建社区时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_test()