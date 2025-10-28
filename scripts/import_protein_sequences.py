#!/usr/bin/env python3
"""
将Protein_renamed.csv文件的数据导入到protein_sequences表中
"""

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import datetime

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

database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

try:
    # 创建数据库引擎
    engine = create_engine(database_url)
    
    # 清空现有数据
    print("正在清空protein_sequences表中的现有数据...")
    with engine.connect() as conn:
        result = conn.execute(text("DELETE FROM protein_sequences"))
        conn.commit()
        print(f"已删除 {result.rowcount} 条记录")
    
    # 读取CSV文件
    csv_file_path = "/home/axlhuang/BioCrew/data/Protein_renamed.csv"
    print(f"正在读取CSV文件: {csv_file_path}")
    
    # 获取文件总行数
    with open(csv_file_path, 'r') as f:
        total_lines = sum(1 for line in f) - 1  # 减去标题行
    print(f"CSV文件包含 {total_lines} 条记录")
    
    # 分块读取CSV文件以避免内存问题
    chunk_size = 100000
    total_inserted = 0
    
    # 分块处理CSV文件
    for chunk in pd.read_csv(csv_file_path, chunksize=chunk_size):
        # 重命名列以匹配数据库表结构
        chunk.rename(columns={
            'Species': 'species_name',
            'Sequence_ID': 'sequence_id',
            'AA_Sequence': 'aa_sequence'
        }, inplace=True)
        
        # 添加序列长度
        chunk['sequence_length'] = chunk['aa_sequence'].str.len()
        
        # 添加时间戳
        chunk['created_at'] = datetime.now()
        chunk['updated_at'] = datetime.now()
        
        # 插入数据
        chunk.to_sql('protein_sequences', engine, if_exists='append', index=False, method='multi')
        total_inserted += len(chunk)
        print(f"已插入 {total_inserted}/{total_lines} 条记录")
    
    print(f"成功插入 {total_inserted} 条记录")
    
    # 验证导入结果
    print("验证导入结果...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM protein_sequences"))
        count = result.fetchone()[0]
        print(f"protein_sequences表中现在共有 {count} 条记录")
        
        # 显示前5条记录
        print("\n导入后的前5条记录:")
        print("-" * 80)
        result = conn.execute(text("SELECT * FROM protein_sequences LIMIT 5"))
        for row in result:
            print(f"ID: {row.id}")
            print(f"物种名: {row.species_name}")
            print(f"序列ID: {row.sequence_id}")
            print(f"氨基酸序列长度: {row.sequence_length}")
            print(f"氨基酸序列: {row.aa_sequence[:50]}...")
            print("-" * 40)
    
    print("蛋白质序列数据导入完成!")
    
except Exception as e:
    print(f"操作过程中发生错误: {e}")
    import traceback
    traceback.print_exc()