#!/usr/bin/env python3
"""
查询RDS数据库中微生物互补性表的前5条记录
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 加载环境变量
load_dotenv()

# 从环境变量获取数据库配置
db_type = os.getenv('DB_TYPE', 'postgresql')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

print(f"数据库配置:")
print(f"  类型: {db_type}")
print(f"  主机: {db_host}")
print(f"  端口: {db_port}")
print(f"  数据库名: {db_name}")
print(f"  用户名: {db_user}")
# print(f"  密码: {db_password}")  # 不打印密码

database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

try:
    # 创建数据库引擎
    engine = create_engine(database_url)
    
    # 创建会话
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 首先查询表结构
    print("\n查询表结构...")
    columns_result = session.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'microbial_complementarity'"))
    print("表 'microbial_complementarity' 的列信息:")
    for row in columns_result:
        print(f"  {row.column_name}: {row.data_type}")
    
    # 查询前5条记录
    result = session.execute(text("SELECT * FROM microbial_complementarity LIMIT 5"))
    
    # 打印结果
    print("\n微生物互补性表的前5条记录:")
    print("-" * 80)
    for i, row in enumerate(result):
        print(f"记录 {i+1}:")
        # 动态打印所有列的值
        for key in row._mapping.keys():
            print(f"  {key}: {getattr(row, key)}")
        print("-" * 40)
    
    session.close()
    
except Exception as e:
    print(f"查询数据库时发生错误: {e}")