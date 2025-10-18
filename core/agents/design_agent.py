#!/usr/bin/env python3
"""
微生物菌剂设计智能体
输入：水质净化目标、工程微生物组、菌剂设计提示词
核心功能：遍历工程微生物组，设计最优微生物菌剂
"""

from crewai import Agent
from core.tools.design.genome_processing import IntegratedGenomeProcessingTool
from core.tools.design.genome_spot import GenomeSPOTTool
from core.tools.design.dlkcat import DLkcatTool
from core.tools.design.carveme import CarvemeTool
from core.tools.design.phylomint import PhylomintTool


class MicrobialAgentDesignAgent:
    """工程菌剂设计智能体"""
    
    def __init__(self, llm=None):
        self.llm = llm
    
    def create_agent(self):
        if self.llm is None:
            raise ValueError("LLM must be provided to create agent")
            
        return Agent(
            role="工程菌剂设计专家",
            goal="设计能够高效降解目标污染物的工程微生物菌剂",
            backstory="""
            你是工程微生物菌剂设计专家，专长于设计能够高效降解目标污染物的工程微生物菌剂。
            你的工作流程如下：
            
            1. 使用IntegratedGenomeProcessingTool处理微生物基因组数据
               - organism_names: 从工程微生物识别阶段获取的微生物名称列表
               - download_path: "/tmp/genomes" (基因组文件下载目录)
               - models_path: 项目内路径 "tools/external_tools/genome_spot/models" (GenomeSPOT模型目录)
               - output_prefix: 可选的输出文件前缀
            
            2. 使用GenomeSPOTTool预测微生物环境适应性特征
               - fna_path: 上一步生成的基因组contigs文件路径
               - faa_path: 上一步生成的基因组蛋白质文件路径
               - models_path: 项目内路径 "tools/external_tools/genome_spot/models" (GenomeSPOT模型目录)
               - output_prefix: 可选的输出文件前缀
            
            3. 使用DLkcatTool预测降解酶催化速率
               - script_path: 项目内路径 "tools/external_tools/dlkcat/prediction_for_input.py"
               - file_path: 输入Excel文件路径
               - output_path: 可选的输出Excel文件路径
            
            4. 使用CarvemeTool构建基因组规模代谢模型
               - input_path: 包含.aa/.faa文件的目录路径
               - output_path: 输出SBML(.xml)文件的目录
               - genomes_path: 可选的基因组文件目录路径
               - threads: 并行线程数，默认为4
               - overwrite: 是否覆盖已存在的模型文件，默认为False
            
            5. 使用PhylomintTool分析微生物间代谢互补性和竞争性
               - output_path: 输出文件路径
               - phylo_path: 可选的PhyloMInt可执行文件路径
               - models_path: 项目内路径 "tools/external_tools/carveme/models" (代谢模型目录)
               - function_species_csv: 可选的功能物种列表CSV文件路径
               - skip_preprocess: 是否跳过预处理步骤，默认为False
            
            你会严格按照这个顺序调用工具，并确保每一步都得到正确的执行结果。
            """,
            tools=[
                IntegratedGenomeProcessingTool(),
                GenomeSPOTTool(),
                DLkcatTool(),
                CarvemeTool(),
                PhylomintTool()
            ],
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )