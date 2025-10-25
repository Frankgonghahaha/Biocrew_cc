#!/usr/bin/env python3
"""
更新CarvemeTool以支持从SQL数据库获取蛋白质序列
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.design.carveme import CarvemeTool
from core.tools.design.protein_sequence_query_sql import ProteinSequenceQuerySQLTool
import os
import tempfile
import io

def create_faa_from_sql_results(sql_results, output_path):
    """
    根据SQL查询结果创建.faa文件
    
    Args:
        sql_results: SQL查询结果
        output_path: 输出.faa文件路径
        
    Returns:
        str: 创建的.faa文件路径
    """
    if sql_results['status'] != 'success':
        raise Exception(f"SQL查询失败: {sql_results['message']}")
    
    with open(output_path, 'w') as f:
        for i, result in enumerate(sql_results['results']):
            # 使用蛋白质ID作为标识符
            protein_id = result.get('protein_id', f'protein_{i}')
            species_name = result.get('species_name', 'unknown')
            gene_name = result.get('gene_name', 'unknown')
            
            # 写入FASTA格式
            f.write(f">{protein_id} {species_name} {gene_name}\n")
            sequence = result['sequence']
            # 每行写入60个字符
            for j in range(0, len(sequence), 60):
                f.write(sequence[j:j+60] + '\n')
    
    return output_path

class UpdatedCarvemeTool(CarvemeTool):
    """
    更新的CarvemeTool，支持从SQL数据库获取蛋白质序列
    """
    
    def _run_with_sql_query(self, query_sequence: str, output_path: str = None, 
                           min_identity: float = 50.0, max_evalue: float = 1e-5,
                           min_alignment_length: int = 50, limit: int = 100,
                           database_path: str = "protein_sequences.db", 
                           threads: int = 4, overwrite: bool = False) -> dict:
        """
        使用SQL查询结果运行Carveme工具
        
        Args:
            query_sequence: 查询蛋白质序列
            output_path: 输出路径
            min_identity: 最小序列相似度百分比
            max_evalue: 最大E-value阈值
            min_alignment_length: 最小比对长度
            limit: 返回结果数量限制
            database_path: SQL数据库文件路径
            threads: 并行线程数
            overwrite: 是否覆盖已存在的模型文件
            
        Returns:
            dict: 执行结果
        """
        try:
            print(f"[UpdatedCarvemeTool] 使用SQL查询运行Carveme工具")
            
            # 1. 使用SQL工具查询相似蛋白质序列
            sql_tool = ProteinSequenceQuerySQLTool()
            sql_results = sql_tool._run(
                query_sequence=query_sequence,
                min_identity=min_identity,
                max_evalue=max_evalue,
                min_alignment_length=min_alignment_length,
                limit=limit,
                database_path=database_path
            )
            
            if sql_results['status'] != 'success':
                return {
                    "status": "error",
                    "message": f"SQL查询失败: {sql_results['message']}"
                }
            
            if sql_results['total_results'] == 0:
                return {
                    "status": "error",
                    "message": "未找到匹配的蛋白质序列"
                }
            
            print(f"[UpdatedCarvemeTool] 找到 {sql_results['total_results']} 个匹配的蛋白质序列")
            
            # 2. 创建临时.faa文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.faa', delete=False) as tmp_faa:
                faa_file_path = tmp_faa.name
                
            # 根据SQL结果创建.faa文件
            create_faa_from_sql_results(sql_results, faa_file_path)
            print(f"[UpdatedCarvemeTool] 已创建临时.faa文件: {faa_file_path}")
            
            # 3. 创建临时目录用于Carveme处理
            with tempfile.TemporaryDirectory() as tmp_dir:
                # 将.faa文件移动到临时目录
                import shutil
                final_faa_path = os.path.join(tmp_dir, "proteins.faa")
                shutil.move(faa_file_path, final_faa_path)
                
                # 4. 调用原始CarvemeTool处理
                print(f"[UpdatedCarvemeTool] 调用CarvemeTool处理蛋白质序列")
                result = super()._run(
                    input_path=tmp_dir,
                    output_path=output_path,
                    threads=threads,
                    overwrite=overwrite
                )
                
                # 清理临时文件
                try:
                    os.remove(faa_file_path)
                except:
                    pass
                    
                return result
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"处理过程中出错: {str(e)}"
            }

def test_updated_carveme_tool():
    """
    测试更新的CarvemeTool
    """
    print("=== 测试更新的CarvemeTool ===\n")
    
    # 创建工具实例
    tool = UpdatedCarvemeTool()
    
    # 测试查询序列
    query_sequence = "MKTLFVVLGAGGIGAAVAYHLFQAGFPVAVVDFRAPDPAQWVQKYAAQLGVPGLVVNAGQGDPGAAFRQAGFKVLGAGGIGLEIARQLGFKVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGFKVLGAGGIGLEIARQLGF"
    
    # 运行工具
    result = tool._run_with_sql_query(
        query_sequence=query_sequence,
        min_identity=40.0,
        max_evalue=1e-3,
        min_alignment_length=30,
        limit=5,
        database_path="protein_sequences.db"
    )
    
    print(f"执行状态: {result['status']}")
    if result['status'] == 'success':
        print(f"输出路径: {result['data']['output_path']}")
        print(f"模型数量: {result['data']['model_count']}")
        print(f"输出文件: {result['data']['output_files']}")
        if result['data']['invalid_models']:
            print(f"无效模型: {result['data']['invalid_models']}")
    else:
        print(f"错误信息: {result['message']}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_updated_carveme_tool()