
"""
清空微生物互补性表并从CSV文件导入新数据
"""

import os
import pandas as pd
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

database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

try:
    # 创建数据库引擎
    engine = create_engine(database_url)
    
    # 创建会话
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 清空现有数据
    print("正在清空现有数据...")
    result = session.execute(text("DELETE FROM microbial_complementarity"))
    deleted_rows = result.rowcount
    session.commit()
    print(f"已删除 {deleted_rows} 条记录")
    
    # 读取CSV文件
    csv_file_path = "/home/axlhuang/BioCrew/data/Phylomint_renamed.csv"
    print(f"正在读取CSV文件: {csv_file_path}")
    df = pd.read_csv(csv_file_path)
    
    # 显示CSV文件的一些基本信息
    print(f"CSV文件包含 {len(df)} 条记录")
    print("CSV文件列名:", df.columns.tolist())
    print("前5行数据:")
    print(df.head())
    
    # 重命名列以匹配数据库表结构
    df.rename(columns={
        'A': 'degrading_microorganism',
        'B': 'complementary_microorganism',
        'Competition': 'competition_index',
        'Complementarity': 'complementarity_index'
    }, inplace=True)
    
    # 添加ID列（让数据库自动生成）
    # df['id'] = range(1, len(df) + 1)
    
    # 插入数据
    print("正在插入新数据...")
    inserted_count = 0
    
    # 分批插入数据以避免内存问题
    batch_size = 1000
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        # 使用to_sql方法直接插入数据
        batch.to_sql('microbial_complementarity', engine, if_exists='append', index=False, method='multi')
        inserted_count += len(batch)
        print(f"已插入 {inserted_count}/{len(df)} 条记录")
    
    print(f"成功插入 {inserted_count} 条记录")
    
    # 验证导入结果
    print("验证导入结果...")
    result = session.execute(text("SELECT COUNT(*) FROM microbial_complementarity"))
    count = result.fetchone()[0]
    print(f"数据库中现在共有 {count} 条记录")
    
    # 显示前5条记录
    print("导入后的前5条记录:")
    result = session.execute(text("SELECT * FROM microbial_complementarity LIMIT 5"))
    print("-" * 80)
    for row in result:
        print(f"ID: {row.id}")
        print(f"降解功能微生物: {row.degrading_microorganism}")
        print(f"互补微生物: {row.complementary_microorganism}")
        print(f"竞争指数: {row.competition_index}")
        print(f"互补指数: {row.complementarity_index}")
        print("-" * 40)
    
    session.close()
    
    print("数据导入完成!")
    
except Exception as e:
    print(f"操作过程中发生错误: {e}")
    if 'session' in locals():
        session.rollback()
        session.close()