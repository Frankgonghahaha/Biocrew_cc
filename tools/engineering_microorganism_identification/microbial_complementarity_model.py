#!/usr/bin/env python3
"""
微生物互补性数据模型
定义数据库表结构和数据模型
"""

from sqlalchemy import Column, Integer, String, Float, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os

Base = declarative_base()

class MicrobialComplementarity(Base):
    """微生物互补性数据模型"""
    __tablename__ = 'microbial_complementarity'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    degrading_microorganism = Column(String, nullable=False, comment="降解功能微生物")
    complementary_microorganism = Column(String, nullable=False, comment="互补微生物")
    genes = Column(String, nullable=True, comment="相关基因")
    competition_index = Column(Float, nullable=False, comment="竞争指数")
    complementarity_index = Column(Float, nullable=False, comment="互补指数")
    
    def __repr__(self):
        return f"<MicrobialComplementarity(degrading_microorganism='{self.degrading_microorganism}', " \
               f"complementary_microorganism='{self.complementary_microorganism}', " \
               f"competition_index={self.competition_index}, " \
               f"complementarity_index={self.complementarity_index})>"

def init_database(database_url: str):
    """
    初始化数据库
    
    Args:
        database_url: 数据库连接URL
    """
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine

def load_excel_data_to_db(database_url: str, excel_file_path: str):
    """
    将Excel数据加载到数据库
    
    Args:
        database_url: 数据库连接URL
        excel_file_path: Excel文件路径
    """
    try:
        # 读取Excel数据
        df = pd.read_excel(excel_file_path, sheet_name=0)
        
        # 初始化数据库
        engine = init_database(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 清空现有数据（对于PostgreSQL需要先删除所有记录）
        try:
            session.execute(text("DELETE FROM microbial_complementarity"))
            session.commit()
        except Exception as e:
            print(f"清空现有数据时出错: {e}")
            # 回滚事务
            session.rollback()
        
        # 插入新数据
        for _, row in df.iterrows():
            record = MicrobialComplementarity(
                degrading_microorganism=row['降解功能微生物'],
                complementary_microorganism=row['互补微生物'],
                genes=row['基因'],
                competition_index=float(row['Competition']),
                complementarity_index=float(row['Complementarity'])
            )
            session.add(record)
        
        session.commit()
        session.close()
        
        print(f"成功将 {len(df)} 条记录加载到数据库")
        return True
        
    except Exception as e:
        print(f"加载数据到数据库时出错: {e}")
        return False