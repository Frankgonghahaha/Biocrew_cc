#!/usr/bin/env python3
"""
数据库工具工厂
用于创建各种数据库查询工具的实例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class DatabaseToolFactory:
    @staticmethod
    def create_all_tools():
        """
        创建所有数据库工具实例
        """
        try:
            # 导入所有工具类
            from tools.pollutant_data_query_tool import PollutantDataQueryTool
            from tools.gene_data_query_tool import GeneDataQueryTool
            from tools.organism_data_query_tool import OrganismDataQueryTool
            from tools.pollutant_summary_tool import PollutantSummaryTool
            from tools.pollutant_search_tool import PollutantSearchTool
            from tools.envipath_tool import EnviPathTool
            from tools.kegg_tool import KeggTool
            from tools.ncbi_genome_query_tool import NCBIGenomeQueryTool  # 新增的工具
            
            # 创建工具实例
            tools = [
                EnviPathTool(),
                KeggTool(),
                PollutantDataQueryTool(),
                GeneDataQueryTool(),
                OrganismDataQueryTool(),
                PollutantSummaryTool(),
                PollutantSearchTool(),
                NCBIGenomeQueryTool()  # 添加新工具到列表
            ]
            
            return tools
        except Exception as e:
            print(f"创建工具时出错: {e}")
            # 返回部分可用工具
            available_tools = []
            
            # 尝试单独导入每个工具
            tool_classes = [
                ('EnviPathTool', 'envipath_tool'),
                ('KeggTool', 'kegg_tool'),
                ('PollutantDataQueryTool', 'pollutant_data_query_tool'),
                ('GeneDataQueryTool', 'gene_data_query_tool'),
                ('OrganismDataQueryTool', 'organism_data_query_tool'),
                ('PollutantSummaryTool', 'pollutant_summary_tool'),
                ('PollutantSearchTool', 'pollutant_search_tool'),
                ('NCBIGenomeQueryTool', 'ncbi_genome_query_tool')  # 新增的工具
            ]
            
            for tool_name, module_name in tool_classes:
                try:
                    module = __import__(f"tools.{module_name}", fromlist=[tool_name])
                    tool_class = getattr(module, tool_name)
                    available_tools.append(tool_class())
                except Exception as import_error:
                    print(f"无法导入 {tool_name}: {import_error}")
            
            return available_tools

    @staticmethod
    def create_tool(tool_name):
        """
        根据工具名称创建特定工具实例
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具实例或None
        """
        try:
            # 工具名称到模块和类名的映射
            tool_mapping = {
                'EnviPathTool': ('envipath_tool', 'EnviPathTool'),
                'KeggTool': ('kegg_tool', 'KeggTool'),
                'PollutantDataQueryTool': ('pollutant_data_query_tool', 'PollutantDataQueryTool'),
                'GeneDataQueryTool': ('gene_data_query_tool', 'GeneDataQueryTool'),
                'OrganismDataQueryTool': ('organism_data_query_tool', 'OrganismDataQueryTool'),
                'PollutantSummaryTool': ('pollutant_summary_tool', 'PollutantSummaryTool'),
                'PollutantSearchTool': ('pollutant_search_tool', 'PollutantSearchTool'),
                'NCBIGenomeQueryTool': ('ncbi_genome_query_tool', 'NCBIGenomeQueryTool')  # 新增的工具
            }
            
            if tool_name not in tool_mapping:
                raise ValueError(f"未知的工具名称: {tool_name}")
            
            module_name, class_name = tool_mapping[tool_name]
            module = __import__(f"tools.{module_name}", fromlist=[class_name])
            tool_class = getattr(module, class_name)
            return tool_class()
        except Exception as e:
            print(f"创建工具 {tool_name} 时出错: {e}")
            return None