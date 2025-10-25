#!/usr/bin/env python3
"""
查看数据库中所有记录的详细信息
"""

import sqlite3
import os

def check_all_records(db_path="protein_sequences.db"):
    """
    查看数据库中所有记录的详细信息
    
    Args:
        db_path: 数据库文件路径
    """
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查看所有记录
    print("=== 数据库中所有记录 ===")
    cursor.execute("SELECT id, species_name, gene_name, protein_id, sequence_length FROM protein_sequences")
    rows = cursor.fetchall()
    
    print(f"{'ID':<3} {'物种名称':<20} {'基因名称':<15} {'蛋白质ID':<15} {'序列长度':<8}")
    print("-" * 70)
    for row in rows:
        print(f"{row[0]:<3} {row[1]:<20} {row[2] or 'None':<15} {row[3]:<15} {row[4]:<8}")
    
    # 统计信息
    print(f"\n总记录数: {len(rows)}")
    
    # 物种分布
    species_count = {}
    for row in rows:
        species = row[1]
        species_count[species] = species_count.get(species, 0) + 1
    
    print("\n物种分布:")
    for species, count in species_count.items():
        print(f"  {species}: {count} 条记录")
    
    # 基因分布
    gene_count = {}
    for row in rows:
        gene = row[2] or "None"
        gene_count[gene] = gene_count.get(gene, 0) + 1
    
    print("\n基因分布:")
    for gene, count in gene_count.items():
        print(f"  {gene}: {count} 条记录")
    
    conn.close()

if __name__ == "__main__":
    check_all_records()