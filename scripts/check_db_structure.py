#!/usr/bin/env python3
"""
检查蛋白质序列数据库的结构和内容
"""

import sqlite3
import os

def check_database_structure(db_path="protein_sequences.db"):
    """
    检查数据库结构和内容
    
    Args:
        db_path: 数据库文件路径
    """
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查看表结构
    print("=== 数据库表结构 ===")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='protein_sequences'")
    table_info = cursor.fetchone()
    if table_info:
        print(table_info[0])
    else:
        print("未找到protein_sequences表")
    
    # 查看索引
    print("\n=== 数据库索引 ===")
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
    indexes = cursor.fetchall()
    for index in indexes:
        print(f"索引名: {index[0]}")
        if index[1]:
            print(f"SQL: {index[1]}")
        else:
            print("SQL: (系统自动生成的唯一索引)")
        print()
    
    # 查看表中数据示例
    print("=== 数据示例 ===")
    cursor.execute("SELECT id, species_name, gene_name, protein_id, sequence_length FROM protein_sequences LIMIT 5")
    rows = cursor.fetchall()
    
    print(f"{'ID':<5} {'物种名称':<20} {'基因名称':<15} {'蛋白质ID':<20} {'序列长度':<10}")
    print("-" * 75)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<20} {row[2] or 'None':<15} {row[3]:<20} {row[4]:<10}")
    
    # 查看总记录数
    cursor.execute("SELECT COUNT(*) FROM protein_sequences")
    count = cursor.fetchone()[0]
    print(f"\n总记录数: {count}")
    
    # 查看一条完整记录示例
    print("\n=== 完整记录示例 ===")
    cursor.execute("SELECT id, species_name, gene_name, protein_id, sequence_length, description, sequence FROM protein_sequences LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"ID: {row[0]}")
        print(f"物种名称: {row[1]}")
        print(f"基因名称: {row[2] or 'None'}")
        print(f"蛋白质ID: {row[3]}")
        print(f"序列长度: {row[4]}")
        print(f"描述: {row[5] or 'None'}")
        print(f"序列: {row[6][:100]}..." if len(row[6]) > 100 else f"序列: {row[6]}")
    
    conn.close()

if __name__ == "__main__":
    check_database_structure()