#!/usr/bin/env python3
"""
微生物互补性查询工具
用于查询预先计算的微生物互补性数据
"""

from crewai.tools import BaseTool
from typing import Type, Optional, List
import pandas as pd
import os
from pydantic import BaseModel, Field


class MicrobialComplementarityQueryToolSchema(BaseModel):
    """微生物互补性查询工具的输入参数"""
    microorganism_a: str = Field(
        description="第一个微生物的名称"
    )
    microorganism_b: Optional[str] = Field(
        default=None,
        description="第二个微生物的名称（可选）"
    )
    gene: Optional[str] = Field(
        default=None,
        description="相关基因名称（可选）"
    )


class MicrobialComplementarityQueryTool(BaseTool):
    name: str = "微生物互补性查询工具"
    description: str = """用于查询预先计算的微生物互补性数据。
    可以根据微生物名称查询其竞争指数和互补指数，避免复杂的代谢模型计算。
    """
    args_schema: Type[BaseModel] = MicrobialComplementarityQueryToolSchema

    def __init__(self):
        super().__init__()
        # 使用__dict__来设置实例属性，避免pydantic的字段验证
        self.__dict__['complementarity_data'] = self._load_complementarity_data()

    def _load_complementarity_data(self) -> pd.DataFrame:
        """
        加载预先计算的互补性数据
        
        Returns:
            包含互补性数据的DataFrame
        """
        try:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建Excel文件路径
            excel_path = os.path.join(current_dir, "..", "工程微生物智能体输出结果.xlsx")
            
            # 检查文件是否存在
            if os.path.exists(excel_path):
                # 读取Excel文件
                df = pd.read_excel(excel_path, sheet_name=0)
                return df
            else:
                # 如果文件不存在，返回空DataFrame
                print(f"文件不存在: {excel_path}")
                return pd.DataFrame()
        except Exception as e:
            print(f"加载互补性数据时出错: {e}")
            return pd.DataFrame()

    def _run(self, microorganism_a: str, microorganism_b: Optional[str] = None, gene: Optional[str] = None) -> str:
        """
        查询微生物互补性数据
        
        Args:
            microorganism_a: 第一个微生物的名称
            microorganism_b: 第二个微生物的名称（可选）
            gene: 相关基因名称（可选）
            
        Returns:
            查询结果的描述字符串
        """
        try:
            # 检查数据是否已加载
            if not hasattr(self, 'complementarity_data') or self.complementarity_data.empty:
                return "未找到预先计算的互补性数据"
            
            # 构建查询条件
            query_conditions = (
                (self.complementarity_data['降解功能微生物'].str.contains(microorganism_a, case=False, na=False)) |
                (self.complementarity_data['互补微生物'].str.contains(microorganism_a, case=False, na=False))
            )
            
            if microorganism_b:
                query_conditions &= (
                    (self.complementarity_data['降解功能微生物'].str.contains(microorganism_b, case=False, na=False)) |
                    (self.complementarity_data['互补微生物'].str.contains(microorganism_b, case=False, na=False))
                )
            
            if gene:
                query_conditions &= self.complementarity_data['基因'].str.contains(gene, case=False, na=False)
            
            # 执行查询
            result_df = self.complementarity_data[query_conditions]
            
            if result_df.empty:
                result = f"未找到关于微生物 '{microorganism_a}'"
                if microorganism_b:
                    result += f" 和 '{microorganism_b}'"
                if gene:
                    result += f" 与基因 '{gene}'"
                result += " 的互补性数据"
                return result
            
            # 格式化结果
            result = f"找到 {len(result_df)} 条关于微生物互补性的记录:\n\n"
            for _, row in result_df.iterrows():
                result += f"降解功能微生物: {row['降解功能微生物']}\n"
                result += f"互补微生物: {row['互补微生物']}\n"
                result += f"相关基因: {row['基因']}\n"
                result += f"竞争指数 (Competition): {row['Competition']:.4f}\n"
                result += f"互补指数 (Complementarity): {row['Complementarity']:.4f}\n"
                result += "-" * 40 + "\n"
            
            return result
            
        except Exception as e:
            return f"查询微生物互补性数据时发生错误: {str(e)}"

    def _arun(self, microorganism_a: str, microorganism_b: Optional[str] = None, gene: Optional[str] = None) -> str:
        """异步运行方法"""
        return self._run(microorganism_a, microorganism_b, gene)