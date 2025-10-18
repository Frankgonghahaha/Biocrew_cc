#!/usr/bin/env python3
"""
微生物互补性数据库查询工具
用于查询存储在数据库中的微生物互补性数据
"""

from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from core.tools.database.complementarity_model import MicrobialComplementarity, init_database
import os


class MicrobialComplementarityDBQueryToolSchema(BaseModel):
    """微生物互补性数据库查询工具的输入参数"""
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


class MicrobialComplementarityDBQueryTool(BaseTool):
    name: str = "微生物互补性数据库查询工具"
    description: str = """用于查询存储在数据库中的微生物互补性数据。
    可以根据微生物名称查询其竞争指数和互补指数，避免复杂的代谢模型计算。
    """
    args_schema: Type[BaseModel] = MicrobialComplementarityDBQueryToolSchema

    def __init__(self):
        super().__init__()
        # 使用__dict__来设置实例属性，避免pydantic的字段验证
        # 从环境变量获取数据库配置
        db_type = os.getenv('DB_TYPE', 'sqlite')
        if db_type == 'postgresql':
            db_host = os.getenv('DB_HOST')
            db_port = os.getenv('DB_PORT')
            db_name = os.getenv('DB_NAME')
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            database_url = 'sqlite:///complementarity.db'
            
        self.__dict__['database_url'] = database_url
        # 初始化数据库
        try:
            engine = init_database(database_url)
            self.__dict__['engine'] = engine
            self.__dict__['Session'] = sessionmaker(bind=engine)
        except Exception as e:
            print(f"初始化数据库时出错: {e}")
            self.__dict__['engine'] = None
            self.__dict__['Session'] = None

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
            # 检查数据库连接
            if not self.__dict__.get('Session'):
                return "数据库连接未初始化"
            
            session = self.__dict__['Session']()
            
            # 构建查询条件
            # 查找microorganism_a作为降解功能微生物或互补微生物的记录
            conditions = [
                MicrobialComplementarity.degrading_microorganism.contains(microorganism_a),
                MicrobialComplementarity.complementary_microorganism.contains(microorganism_a)
            ]
            query_conditions = or_(*conditions)
            
            if microorganism_b:
                # 查找microorganism_b作为降解功能微生物或互补微生物的记录
                conditions_b = [
                    MicrobialComplementarity.degrading_microorganism.contains(microorganism_b),
                    MicrobialComplementarity.complementary_microorganism.contains(microorganism_b)
                ]
                query_conditions = and_(
                    query_conditions,
                    or_(*conditions_b)
                )
            
            if gene:
                query_conditions = and_(
                    query_conditions,
                    MicrobialComplementarity.genes.contains(gene)
                )
            
            # 执行查询
            results = session.query(MicrobialComplementarity).filter(query_conditions).all()
            
            session.close()
            
            if not results:
                result = f"未找到关于微生物 '{microorganism_a}'"
                if microorganism_b:
                    result += f" 和 '{microorganism_b}'"
                if gene:
                    result += f" 与基因 '{gene}'"
                result += " 的互补性数据"
                return result
            
            # 格式化结果
            result = f"找到 {len(results)} 条关于微生物互补性的记录:\n\n"
            for record in results:
                result += f"降解功能微生物: {record.degrading_microorganism}\n"
                result += f"互补微生物: {record.complementary_microorganism}\n"
                result += f"相关基因: {record.genes}\n"
                result += f"竞争指数 (Competition): {record.competition_index:.4f}\n"
                result += f"互补指数 (Complementarity): {record.complementarity_index:.4f}\n"
                result += "-" * 40 + "\n"
            
            return result
            
        except Exception as e:
            return f"查询微生物互补性数据时发生错误: {str(e)}"

    def _arun(self, microorganism_a: str, microorganism_b: Optional[str] = None, gene: Optional[str] = None) -> str:
        """异步运行方法"""
        return self._run(microorganism_a, microorganism_b, gene)