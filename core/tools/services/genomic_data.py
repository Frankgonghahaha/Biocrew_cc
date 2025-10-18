#!/usr/bin/env python3
"""
基因组数据服务
提供从不同来源（URL、文件、字符串）读取基因组序列的功能
"""

import io
import gzip
import requests
import os
from typing import Optional, Union
from Bio import SeqIO


class GenomicDataService:
    """
    基因组数据服务类，支持从URL、文件或字符串读取基因组序列
    """
    
    def __init__(self, cache_dir: str = "/tmp/genomic_cache"):
        """
        初始化基因组数据服务
        
        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def load_sequences(self, source: Union[str, io.StringIO, io.BytesIO], file_type: str = "fasta") -> list:
        """
        从不同来源加载序列
        
        Args:
            source: 序列源，可以是URL、文件路径或序列字符串
            file_type: 文件类型 (fasta, genbank等)
            
        Returns:
            list: 序列列表
        """
        # 如果source是StringIO或BytesIO对象，直接解析
        if isinstance(source, (io.StringIO, io.BytesIO)):
            return list(SeqIO.parse(source, file_type))
            
        # 如果是字符串且以>开头，认为是序列字符串
        if isinstance(source, str) and source.startswith('>'):
            seq_io = io.StringIO(source)
            return list(SeqIO.parse(seq_io, file_type))
            
        # 如果是URL
        elif isinstance(source, str) and source.startswith(('http://', 'https://')):
            return self._load_from_url(source, file_type)
            
        # 如果是文件路径
        else:
            return self._load_from_file(source, file_type)
    
    def _load_from_url(self, url: str, file_type: str = "fasta") -> list:
        """
        从URL加载序列数据
        
        Args:
            url: 序列文件的URL
            file_type: 文件类型
            
        Returns:
            list: 序列列表
        """
        try:
            # 检查缓存
            cached_file = self._get_cached_file_path(url)
            if os.path.exists(cached_file):
                return self._load_from_file(cached_file, file_type)
            
            # 从网络下载
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # 处理gzip文件
            if url.endswith('.gz'):
                content = gzip.decompress(response.content)
                seq_io = io.BytesIO(content)
            else:
                seq_io = io.StringIO(response.text)
            
            sequences = list(SeqIO.parse(seq_io, file_type))
            
            # 缓存文件
            self._cache_file(url, response.content)
            
            return sequences
            
        except Exception as e:
            print(f"[GenomicDataService] 从URL加载序列失败: {e}")
            raise
    
    def _load_from_file(self, file_path: str, file_type: str = "fasta") -> list:
        """
        从文件加载序列
        
        Args:
            file_path: 文件路径
            file_type: 文件类型
            
        Returns:
            list: 序列列表
        """
        try:
            # 处理gzip文件
            if file_path.endswith('.gz'):
                with gzip.open(file_path, 'rt') as handle:
                    return list(SeqIO.parse(handle, file_type))
            else:
                with open(file_path, 'r') as handle:
                    return list(SeqIO.parse(handle, file_type))
        except Exception as e:
            print(f"[GenomicDataService] 从文件加载序列失败: {e}")
            raise
    
    def _get_cached_file_path(self, url: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            url: URL
            
        Returns:
            str: 缓存文件路径
        """
        # 使用URL的hash作为文件名
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, url_hash)
    
    def _cache_file(self, url: str, content: bytes):
        """
        缓存文件
        
        Args:
            url: URL
            content: 文件内容
        """
        try:
            cached_file = self._get_cached_file_path(url)
            with open(cached_file, 'wb') as f:
                f.write(content)
        except Exception as e:
            print(f"[GenomicDataService] 缓存文件失败: {e}")
    
    def get_genomic_data_urls(self, assembly_accession: str) -> dict:
        """
        根据Assembly Accession获取基因组数据URL
        
        Args:
            assembly_accession: Assembly Accession号
            
        Returns:
            dict: 包含contigs和proteins URL的字典
        """
        # 构造FTP路径
        # 例如: GCF_000014565.1 -> https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/014/565/GCF_000014565.1_ASM1456v1
        parts = assembly_accession.split('.')
        prefix = parts[0]
        path_parts = [prefix[i:i+3] for i in range(0, len(prefix), 3)]
        path_parts = [part for part in path_parts if part]  # 移除空字符串
        
        ftp_path = f"https://ftp.ncbi.nlm.nih.gov/genomes/all/{'/'.join(path_parts)}/{assembly_accession}"
        
        # 构造URL
        contigs_url = f"{ftp_path}/{assembly_accession}_genomic.fna.gz"
        proteins_url = f"{ftp_path}/{assembly_accession}_protein.faa.gz"
        
        return {
            "contigs": contigs_url,
            "proteins": proteins_url
        }


def test_genomic_data_service():
    """
    测试基因组数据服务
    """
    print("=== 测试基因组数据服务 ===\n")
    
    service = GenomicDataService()
    
    # 测试1: 使用序列字符串
    print("[测试1] 使用序列字符串")
    mock_contigs = """>mock_contig_1
ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC
>mock_contig_2
GCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCA"""
    
    sequences = service.load_sequences(mock_contigs)
    print(f"成功加载 {len(sequences)} 条序列\n")
    
    # 测试2: 获取基因组数据URL
    print("[测试2] 获取基因组数据URL")
    urls = service.get_genomic_data_urls("GCF_000014565.1")
    print(f"Contigs URL: {urls['contigs']}")
    print(f"Proteins URL: {urls['proteins']}\n")
    
    print("=== 测试完成 ===")


if __name__ == "__main__":
    test_genomic_data_service()