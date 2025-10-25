#!/usr/bin/env python3
"""
初始化蛋白质序列数据库脚本
创建SQLite数据库并插入示例蛋白质序列数据
"""

import sqlite3
import os

def create_protein_database(db_path="protein_sequences.db"):
    """
    创建蛋白质序列数据库
    
    Args:
        db_path: 数据库文件路径
    """
    # 如果数据库文件已存在，先删除
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建蛋白质序列表
    cursor.execute('''
        CREATE TABLE protein_sequences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            species_name TEXT NOT NULL,
            gene_name TEXT,
            protein_id TEXT UNIQUE NOT NULL,
            sequence TEXT NOT NULL,
            sequence_length INTEGER NOT NULL,
            description TEXT
        )
    ''')
    
    # 创建索引以提高查询性能
    cursor.execute('''
        CREATE INDEX idx_sequence_length ON protein_sequences(sequence_length)
    ''')
    
    cursor.execute('''
        CREATE INDEX idx_species_name ON protein_sequences(species_name)
    ''')
    
    cursor.execute('''
        CREATE INDEX idx_protein_id ON protein_sequences(protein_id)
    ''')
    
    # 插入示例数据
    sample_proteins = [
        ("Pseudomonas putida", "alkB", "ALKB_PSEPU", 
         "MKTLFVVLGAGGIGAAVAYHLFQAGFPVAVVDFRAPDPAQWVQKYAAQLGVPGLVVNAGQGDPGAAFRQAGFKVLGAGGIGLEIARQLGFKVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGFKVLGAGGIGLEIARQLGF", 
         "烷烃羟化酶，参与烷烃降解"),
        ("Pseudomonas putida", "alkG", "ALKG_PSEPU", 
         "MKAFILPRVLSLVLLGAAFAAQAQDVTATPYKRLRRAQRSLGESVQVNDLVFGDPAFADLVFGDPAYADLVFGDPAFADLVFGDPAYADLVFGDPAYADLVFGDPAFADLVFGDPAYADLVFGDPAFADLVFGDPAYADLVFGDPAFADLVFGD", 
         "烷烃羟化酶还原酶组分"),
        ("Rhodococcus jostii", "bioA", "BIOA_RHOJZ", 
         "MTDLRPAVRLGLGPMGLRGVLRQAGFKVLGAGGIGLEIARQLGFKVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGFKVLGAGGIGLEIARQLGFQVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGF", 
         "生物素合成酶A"),
        ("Rhodococcus jostii", "bioB", "BIOB_RHOJZ", 
         "MRVLPAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAA", 
         "生物素合成酶B"),
        ("Pseudomonas putida", "xylX", "XYLX_PSEPU", 
         "MKDLQPTVLLALALGAAFAAQAQDVTATPYKRLRRAQRSLGESVQVNDLVFGDPAFADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGD", 
         "二甲苯单加氧酶组分"),
        ("Pseudomonas putida", "xylY", "XYLY_PSEPU", 
         "MKAFILPRVLSLVLLGAAFAAQAQDVTATPYKRLRRAQRSLGESVQVNDLVFGDPAFADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGD", 
         "二甲苯单加氧酶还原酶组分"),
        ("Rhodococcus jostii", "nidA", "NIDA_RHOJZ", 
         "MRVLPAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAARLGAVPGTAAA", 
         "芳香环羟化酶α亚基"),
        ("Rhodococcus jostii", "nidB", "NIDB_RHOJZ", 
         "MTDLRPAVRLGLGPMGLRGVLRQAGFKVLGAGGIGLEIARQLGFKVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGFKVLGAGGIGLEIARQLGFQVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGF", 
         "芳香环羟化酶β亚基"),
        ("Pseudomonas putida", "todC1", "TODC1_PSEPU", 
         "MKTLFVVLGAGGIGAAVAYHLFQAGFPVAVVDFRAPDPAQWVQKYAAQLGVPGLVVNAGQGDPGAAFRQAGFKVLGAGGIGLEIARQLGFKVTVVDFRAPDPGKWVQKYGQQVGLPGLVVNAGQGDPGAALRQAGFKVLGAGGIGLEIARQLGF", 
         "甲苯双加氧酶铁氧还蛋白组分"),
        ("Pseudomonas putida", "todC2", "TODC2_PSEPU", 
         "MKAFILPRVLSLVLLGAAFAAQAQDVTATPYKRLRRAQRSLGESVQVNDLVFGDPAFADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGDPAYADLVFGD", 
         "甲苯双加氧酶铁氧还蛋白还原酶组分"),
    ]
    
    # 插入数据
    for species_name, gene_name, protein_id, sequence, description in sample_proteins:
        cursor.execute('''
            INSERT INTO protein_sequences 
            (species_name, gene_name, protein_id, sequence, sequence_length, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (species_name, gene_name, protein_id, sequence, len(sequence), description))
    
    # 提交更改并关闭连接
    conn.commit()
    conn.close()
    
    print(f"蛋白质序列数据库已创建: {db_path}")
    print(f"插入了 {len(sample_proteins)} 条示例蛋白质序列记录")

def query_database_example(db_path="protein_sequences.db"):
    """
    查询数据库示例
    
    Args:
        db_path: 数据库文件路径
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询所有记录
    cursor.execute("SELECT * FROM protein_sequences")
    results = cursor.fetchall()
    
    print("\n数据库中的蛋白质序列记录:")
    print("-" * 80)
    for row in results:
        print(f"ID: {row[0]}")
        print(f"物种: {row[1]}")
        print(f"基因: {row[2]}")
        print(f"蛋白质ID: {row[3]}")
        print(f"序列长度: {row[4]}")
        print(f"描述: {row[5]}")
        print(f"序列: {row[6][:50]}..." if len(row[6]) > 50 else f"序列: {row[6]}")
        print("-" * 80)
    
    conn.close()

if __name__ == "__main__":
    # 创建数据库
    create_protein_database()
    
    # 查询示例
    query_database_example()