#!/usr/bin/env python3
"""
测试API端点的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

def test_endpoints():
    """测试API端点"""
    client = TestClient(app)
    
    # 测试根端点
    print("测试根端点...")
    response = client.get("/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 测试获取用户对话历史端点
    print("\n测试获取用户对话历史端点...")
    response = client.get("/api/users/1/conversations")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"响应: {response.json()}")
    else:
        print(f"错误: {response.text}")
    
    # 测试获取用户安全日志端点
    print("\n测试获取用户安全日志端点...")
    response = client.get("/api/users/1/security-logs")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"响应: {response.json()}")
    else:
        print(f"错误: {response.text}")

if __name__ == "__main__":
    test_endpoints()