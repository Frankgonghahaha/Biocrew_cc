from crewai import Agent

from core.tools.evaluation.parse3_json_tool import ParseDesignConsortiaTool
from core.tools.evaluation.faa_build_tool import FaaBuildTool
from core.tools.evaluation.carveme_tool import CarvemeModelBuildTool
from core.tools.evaluation.medium_tool import MediumBuildTool
from core.tools.evaluation.add_pathway_tool import AddPathwayTool
from core.tools.evaluation.micom_tool import MicomSimulationTool


class MicrobialAgentEvaluationAgent:
    def __init__(self, llm):
        self.llm = llm

    def create_agent(self):
        tools = [
            ParseDesignConsortiaTool(),
            FaaBuildTool(),
            CarvemeModelBuildTool(),
            MediumBuildTool(),
            AddPathwayTool(),
            MicomSimulationTool(),
        ]

        return Agent(
            role='菌剂评估专家',
            goal='评估微生物菌剂的生物净化效果和生态特性',
            backstory="""你是一位菌剂评估专家，专注于评估微生物菌剂的净化效果和生态特性。
            你根据微生物菌剂、水质净化目标（含生态预期值）、污水厂水质背景进行综合评估。""",
            tools=tools,
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
        )
