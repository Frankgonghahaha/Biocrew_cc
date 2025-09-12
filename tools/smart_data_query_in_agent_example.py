#!/usr/bin/env python3
"""
智能数据查询工具在Agent中的使用示例
展示如何在工程微生物组识别智能体中集成和使用智能数据查询工具
"""

from crewai import Agent, Task, Crew
from tools.smart_data_query_tool import SmartDataQueryTool

class SmartEngineeringMicroorganismIdentificationAgent:
    def __init__(self, llm):
        self.llm = llm
        # 初始化智能数据查询工具
        self.smart_query = SmartDataQueryTool()
    
    def query_relevant_data(self, user_request):
        """
        根据用户请求查询相关数据
        
        Args:
            user_request (str): 用户请求
            
        Returns:
            str: 格式化的数据上下文供LLM使用
        """
        # 使用智能数据查询工具自动识别并查询相关数据
        query_result = self.smart_query.query_related_data(user_request)
        
        if query_result["status"] != "success":
            return "未找到相关数据"
        
        # 构建数据上下文
        context = "根据您的请求，我找到了以下相关数据:\n\n"
        
        # 添加基因数据信息
        if query_result["gene_data"]:
            context += "基因数据:\n"
            for pollutant, data_info in query_result["gene_data"].items():
                if "error" not in data_info:
                    context += f"- {pollutant}: {data_info['shape'][0]}行{data_info['shape'][1]}列\n"
                    # 添加示例数据
                    if "sample_data" in data_info:
                        context += "  示例数据:\n"
                        for i, row in enumerate(data_info["sample_data"]):
                            context += f"    行{i+1}: {str(row)[:100]}...\n"
                else:
                    context += f"- {pollutant}: 查询出错 ({data_info['error']})\n"
        
        # 添加微生物数据信息
        if query_result["organism_data"]:
            context += "\n微生物数据:\n"
            for pollutant, data_info in query_result["organism_data"].items():
                if "error" not in data_info:
                    context += f"- {pollutant}: {data_info['shape'][0]}行{data_info['shape'][1]}列\n"
                    # 添加示例数据
                    if "sample_data" in data_info:
                        context += "  示例数据:\n"
                        for i, row in enumerate(data_info["sample_data"]):
                            context += f"    行{i+1}: {str(row)[:100]}...\n"
                else:
                    context += f"- {pollutant}: 查询出错 ({data_info['error']})\n"
        
        return context
    
    def create_agent(self):
        """
        创建智能工程微生物组识别智能体
        """
        return Agent(
            role='智能功能微生物组识别专家',
            goal='根据水质净化目标自动识别并查询相关数据，筛选功能微生物和代谢互补微生物',
            backstory="""你是一位智能功能微生物组识别专家，具备以下能力：
            1. 能够自动识别用户请求中的污染物名称
            2. 能够从本地数据目录智能查询相关基因和微生物数据
            3. 能够调用Tool_api工具拉取基因组/酶序列数据
            4. 能够使用Tool_Carveme工具将基因组转为代谢模型
            5. 能够基于互补指数和竞争指数筛选功能微生物
            
            当用户提出请求时，你会首先自动查询相关数据，然后基于数据进行分析。""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_task(self, agent, user_request):
        """
        创建任务，集成智能数据查询功能
        
        Args:
            agent: 智能体实例
            user_request (str): 用户请求
            
        Returns:
            Task: 任务实例
        """
        # 查询相关数据
        data_context = self.query_relevant_data(user_request)
        
        description = f"""
        根据用户请求识别工程微生物组，并提供详细分析。
        
        用户请求：{user_request}
        
        相关数据：
        {data_context}
        
        请基于以上数据，按照以下步骤进行分析：
        1. 分析水质净化目标（水质治理指标+目标污染物）
        2. 基于查询到的基因和微生物数据，筛选功能微生物
        3. 计算竞争指数和互补指数
        4. 按"互补指数＞竞争指数"的原则筛选功能微生物+代谢互补微生物
        """
        
        expected_output = """
        提供完整的工程微生物组识别报告，包括：
        1. 识别的功能微生物列表
        2. 代谢互补微生物列表
        3. 竞争指数和互补指数计算结果
        4. 微生物组选择的科学依据
        5. 基于查询数据的具体分析结果
        """
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            verbose=True
        )

# 使用示例
if __name__ == "__main__":
    # 这个示例展示了如何在实际应用中使用智能数据查询工具
    print("智能数据查询工具在Agent中的使用示例")
    print("=" * 50)
    
    # 模拟用户请求
    user_requests = [
        "我们需要处理Alpha-hexachlorocyclohexane污染的工业废水",
        "请分析含有Pentachlorophenol的污水并推荐微生物处理方案",
        "如何处理含有多氯联苯(PCBs)的污水？"
    ]
    
    # 创建智能数据查询工具实例
    smart_query = SmartDataQueryTool()
    
    for i, request in enumerate(user_requests, 1):
        print(f"\n示例 {i}: {request}")
        print("-" * 30)
        
        # 查询相关数据
        result = smart_query.query_related_data(request)
        
        if result["status"] == "success":
            print(f"匹配的污染物数量: {len(result['matched_pollutants'])}")
            print(f"成功查询的基因数据项数: {len([k for k, v in result['gene_data'].items() if 'error' not in v])}")
            print(f"成功查询的微生物数据项数: {len([k for k, v in result['organism_data'].items() if 'error' not in v])}")
            
            # 显示前几个匹配的污染物
            print(f"匹配的污染物: {result['matched_pollutants'][:3]}...")
        else:
            print("未找到相关数据")
    
    print("\n" + "=" * 50)
    print("使用说明:")
    print("1. 在实际应用中，这个工具会集成到智能体的思考过程中")
    print("2. 当用户提出请求时，智能体会自动调用query_relevant_data方法")
    print("3. 查询到的数据会作为上下文提供给LLM进行分析")
    print("4. LLM基于数据和专业知识生成最终的分析报告")
