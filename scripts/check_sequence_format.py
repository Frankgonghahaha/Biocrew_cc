#!/usr/bin/env python3
"""
详细查看数据库中的序列数据格式
"""

import sqlite3
import os

def check_sequence_data_format(db_path="protein_sequences.db"):
    """
    详细查看数据库中的序列数据格式
    
    Args:
        db_path: 数据库文件路径
    """
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查看几条完整的序列数据
    print("=== 序列数据格式详情 ===")
    cursor.execute("SELECT id, protein_id, sequence, sequence_length FROM protein_sequences LIMIT 3")
    rows = cursor.fetchall()
    
    for i, row in enumerate(rows, 1):
        print(f"\n--- 记录 {i} ---")
        print(f"ID: {row[0]}")
        print(f"蛋白质ID: {row[1]}")
        print(f"序列长度: {row[3]}")
        print(f"序列内容: {row[2]}")
        print(f"序列长度验证: {len(row[2])} (实际长度)")
        print(f"长度匹配: {'是' if len(row[2]) == row[3] else '否'}")
    
    # 检查序列字符组成
    print("\n=== 序列字符组成分析 ===")
    cursor.execute("SELECT sequence FROM protein_sequences LIMIT 1")
    sequence = cursor.fetchone()[0]
    
    # 统计字符频率
    char_count = {}
    for char in sequence:
        char_count[char] = char_count.get(char, 0) + 1
    
    print(f"序列长度: {len(sequence)}")
    print(f"唯一字符数: {len(char_count)}")
    print("字符频率统计:")
    for char, count in sorted(char_count.items()):
        print(f"  {char}: {count}")
    
    conn.close()

if __name__ == "__main__":
    check_sequence_data_format()