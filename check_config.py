#!/usr/bin/env python3
"""
配置检查脚本
用于验证.env文件是否正确配置
"""

import os
from dotenv import load_dotenv
from config.config import Config

def check_env_file():
    """检查.env文件是否存在"""
    if not os.path.exists('.env'):
        print("❌ 未找到.env文件")
        print("请执行以下命令创建.env文件:")
        print("  cp .env.example .env")
        print("然后编辑.env文件，填入实际的API配置信息")
        return False
    else:
        print("✅ .env文件存在")
        return True

def check_env_variables():
    """检查环境变量配置"""
    load_dotenv()
    
    issues = []
    
    # 检查API基础URL
    if Config.QWEN_API_BASE == 'YOUR_API_BASE_URL' or 'your-qwen-api-endpoint' in Config.QWEN_API_BASE:
        issues.append("QWEN_API_BASE未正确配置，请替换为实际的API地址")
    
    # 检查API密钥
    if Config.QWEN_API_KEY == 'YOUR_API_KEY' or 'your-api-key' in Config.QWEN_API_KEY:
        issues.append("QWEN_API_KEY未正确配置，请替换为实际的API密钥")
    
    # 检查模型名称
    if Config.QWEN_MODEL_NAME == 'QWEN3':
        print("⚠️  建议使用完整模型名称格式，如 'openai/QWEN3'")
    
    if issues:
        print("❌ 配置问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ 环境变量配置检查通过")
        print(f"  QWEN_API_BASE: {Config.QWEN_API_BASE}")
        print(f"  QWEN_MODEL_NAME: {Config.QWEN_MODEL_NAME}")
        print(f"  VERBOSE: {Config.VERBOSE}")
        return True

def check_api_connectivity():
    """检查API连接性（可选）"""
    print("\n💡 提示: 可以通过运行测试脚本来验证API连接性:")
    print("  python test_system.py")

def main():
    print("BioCrew配置检查工具")
    print("=" * 30)
    
    env_file_ok = check_env_file()
    if not env_file_ok:
        return
    
    config_ok = check_env_variables()
    if not config_ok:
        return
    
    print("\n✅ 所有配置检查通过!")
    print("\n接下来您可以:")
    print("1. 运行测试脚本验证系统功能:")
    print("   python test_system.py")
    print("2. 或者运行主程序:")
    print("   python main.py")

if __name__ == "__main__":
    main()