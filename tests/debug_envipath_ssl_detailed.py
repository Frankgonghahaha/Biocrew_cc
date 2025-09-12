#!/usr/bin/env python3
"""
EnviPath SSL问题详细诊断脚本
"""

import requests
import ssl
import socket
from urllib.parse import urlparse

def test_different_ssl_contexts(url):
    """测试不同的SSL上下文配置"""
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    port = parsed_url.port or 443
    
    print(f"测试不同的SSL上下文配置: {hostname}:{port}")
    
    # 测试不同的TLS版本
    tls_versions = [
        (ssl.PROTOCOL_TLSv1, "TLSv1"),
        (ssl.PROTOCOL_TLSv1_1, "TLSv1.1"),
        (ssl.PROTOCOL_TLSv1_2, "TLSv1.2"),
    ]
    
    for protocol, name in tls_versions:
        try:
            print(f"  测试 {name}...")
            context = ssl.SSLContext(protocol)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((hostname, port), timeout=30) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    print(f"    {name} 连接成功")
        except Exception as e:
            print(f"    {name} 失败: {e}")
    
    # 测试默认上下文
    try:
        print(f"  测试默认SSL上下文...")
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((hostname, port), timeout=30) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print(f"    默认上下文连接成功")
    except Exception as e:
        print(f"    默认上下文失败: {e}")

def test_requests_with_different_configs(url):
    """测试requests的不同配置"""
    print(f"测试requests的不同配置: {url}")
    
    # 配置1: 禁用SSL验证
    try:
        print("  配置1: 禁用SSL验证...")
        session = requests.Session()
        session.verify = False
        response = session.get(url, timeout=30)
        print(f"    成功，状态码: {response.status_code}")
    except Exception as e:
        print(f"    失败: {e}")
    
    # 配置2: 使用不同的TLS版本
    try:
        print("  配置2: 使用TLSv1.2...")
        from requests.adapters import HTTPAdapter
        from urllib3.util.ssl_ import create_urllib3_context
        
        class TLSAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                ctx = create_urllib3_context()
                ctx.set_ciphers('DEFAULT@SECLEVEL=1')
                kwargs['ssl_context'] = ctx
                return super().init_poolmanager(*args, **kwargs)
        
        session = requests.Session()
        session.mount('https://', TLSAdapter())
        response = session.get(url, timeout=30)
        print(f"    成功，状态码: {response.status_code}")
    except Exception as e:
        print(f"    失败: {e}")

def main():
    print("EnviPath SSL问题详细诊断")
    print("=" * 30)
    
    test_url = "https://envipath.ethz.ch/"
    print(f"测试URL: {test_url}")
    print("-" * 20)
    
    # 测试不同的SSL上下文
    test_different_ssl_contexts(test_url)
    
    print()
    
    # 测试requests的不同配置
    test_requests_with_different_configs(test_url)

if __name__ == "__main__":
    main()