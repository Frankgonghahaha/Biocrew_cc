#!/usr/bin/env python3
"""
微生物菌剂设计任务
输入：水质净化目标、工程微生物组、菌剂设计提示词
核心功能：遍历工程微生物组，设计最优微生物菌剂
"""

class MicrobialAgentDesignTask:
    def __init__(self, llm):
        self.llm = llm

    def create_task(self, agent, context_task=None, feedback=None, user_requirement=None):
        from crewai import Task
        
        description = """
        根据工程微生物组设计功能微生物菌剂配方，确保菌剂具有高效的污染物降解能力和良好的生态稳定性。
        
        设计步骤：
        1. 分析目标污染物特性和处理要求，包括浓度范围、处理时间、环境条件等
        2. 遍历工程微生物组，组合功能菌+互补菌形成候选群落
        3. 使用基因组数据构建每个微生物的代谢模型
        4. 基于代谢模型分析各候选群落的降解潜力
        5. 评估候选群落的代谢互补性和生态稳定性
        6. 选择降解潜力最高且稳定性良好的候选群落作为最优菌剂
        7. 优化菌剂配比以确保群落稳定性和结构稳定性
        8. 预测菌剂在实际应用中的性能表现
        
        工具使用策略：
        1. 使用IntegratedGenomeProcessingTool处理微生物基因组数据，包括查询、下载和分析
        2. 使用GenomeSPOTTool预测微生物的环境适应性特征（温度、pH、盐度和氧气耐受性）
        3. 使用DLkcatTool预测降解酶对于特定底物的降解速率（Kcat值）
        4. 使用CarvemeTool构建基因组规模代谢模型(GSMM)
        5. 综合分析所有工具的结果，形成完整的菌剂设计方案
        
        关键参数：
        - 权衡系数（0-1，0=保多样性，1=提降解效率）
        - 群落稳定性指数
        - 代谢通量分布均匀性
        """
        
        # 添加用户自定义需求到描述中
        if user_requirement:
            description += f"\n\n用户具体需求：{user_requirement}"
        
        if feedback:
            description += f"\n\n根据评估反馈进行优化设计：\n{feedback}"
        
        expected_output = """
        提供完整的菌剂设计方案，包括：
        1. 菌剂组成（微生物种类和比例）
        2. 设计原理说明（基于代谢模型和生态学原理）
        3. 稳定性保障措施（群落结构优化策略）
        4. 预期的净化效果（降解速率、处理时间等）
        5. 降解潜力分析结果（各微生物的贡献度分析）
        6. 培养基推荐（支持菌剂生长的营养条件）
        7. 应用条件要求（温度、pH、溶解氧等环境参数）
        8. 质量控制指标（菌剂活性检测方法）
        """
        
        # 如果有上下文任务，设置依赖关系
        task_params = {
            'description': description.strip(),
            'expected_output': expected_output.strip(),
            'agent': agent,
            'verbose': True
        }
        
        if context_task:
            task_params['context'] = [context_task]
            
        return Task(**task_params)