#!/usr/bin/env python3
"""
EnviPath SSL问题诊断脚本
"""

import requests
import ssl
import socket
from urllib.parse import urlparse

def test_ssl_handshake(url):
    """测试SSL握手"""
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    port = parsed_url.port or 443
    
    print(f"测试SSL握手: {hostname}:{port}")
    
    try:
        context = ssl.create_default_context()
        # 启用调试信息
        context.set_ciphers('DEFAULT')
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        with socket.create_connection((hostname, port), timeout=30) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print(f"SSL版本: {ssock.version()}")
                cert = ssock.getpeercert()
                print(f"证书信息: {cert['subject']}")
                return True
    except Exception as e:
        print(f"SSL握手失败: {e}")
        return False

def test_requests_connection(url):
    """测试requests连接"""
    print(f"测试requests连接: {url}")
    
    try:
        # 尝试不同的SSL配置
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'BioCrew/1.0 (debug-envipath-ssl)',
            'Accept': 'application/json'
        })
        
        response = session.get(url, timeout=30)
        print(f"连接成功，状态码: {response.status_code}")
        return True
    except requests.exceptions.SSLError as e:
        print(f"SSL错误: {e}")
        return False
    except Exception as e:
        print(f"其他错误: {e}")
        return False

def main():
    print("EnviPath SSL问题诊断")
    print("=" * 30)
    
    # 测试URL
    test_urls = [
        "https://envipath.ethz.ch/",
        "https://envipath.ethz.ch/rest/search?query=cadmium"
    ]
    
    for url in test_urls:
        print(f"\n测试URL: {url}")
        print("-" * 20)
        
        # 测试SSL握手
        test_ssl_handshake(url)
        
        # 测试requests连接
        test_requests_connection(url)
        
        print()

if __name__ == "__main__":
    main()