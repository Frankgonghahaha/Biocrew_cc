#!/usr/bin/env python3
"""
数据库工具工厂
用于创建和管理各种数据库查询工具
"""

from tools.envipath_tool import EnviPathTool
from tools.kegg_tool import KeggTool
from tools.pollutant_data_query_tool import PollutantDataQueryTool
from tools.gene_data_query_tool import GeneDataQueryTool
from tools.organism_data_query_tool import OrganismDataQueryTool
from tools.pollutant_summary_tool import PollutantSummaryTool
from tools.ncbi_genome_query_tool import NCBIGenomeQueryTool
from tools.microbial_complementarity_db_query_tool import MicrobialComplementarityDBQueryTool


class DatabaseToolFactory:
    """数据库工具工厂类"""
    
    @staticmethod
    def create_all_tools():
        """
        创建所有数据库工具实例
        
        Returns:
            list: 所有工具实例的列表
        """
        tools = [
            EnviPathTool(),
            KeggTool(),
            PollutantDataQueryTool(),
            GeneDataQueryTool(),
            OrganismDataQueryTool(),
            PollutantSummaryTool(),
            NCBIGenomeQueryTool(),
            MicrobialComplementarityDBQueryTool()
        ]
        
        return tools
    
    @staticmethod
    def create_envi_path_tool():
        """创建EnviPath工具实例"""
        return EnviPathTool()
    
    @staticmethod
    def create_kegg_pathway_tool():
        """创建KEGG通路工具实例"""
        return KeggTool()
    
    @staticmethod
    def create_pollutant_data_query_tool():
        """创建污染物数据查询工具实例"""
        return PollutantDataQueryTool()
    
    @staticmethod
    def create_gene_data_query_tool():
        """创建基因数据查询工具实例"""
        return GeneDataQueryTool()
    
    @staticmethod
    def create_organism_data_query_tool():
        """创建微生物数据查询工具实例"""
        return OrganismDataQueryTool()
    
    @staticmethod
    def create_pollutant_summary_tool():
        """创建污染物摘要工具实例"""
        return PollutantSummaryTool()
    
    @staticmethod
    def create_ncbi_genome_query_tool():
        """创建NCBI基因组查询工具实例"""
        return NCBIGenomeQueryTool()
    
    @staticmethod
    def create_microbial_complementarity_db_query_tool():
        """创建微生物互补性数据库查询工具实例"""
        return MicrobialComplementarityDBQueryTool()