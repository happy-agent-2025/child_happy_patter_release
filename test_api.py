import requests
import json

def test_api():
    # 测试根端点
    print("测试根端点...")
    response = requests.get("http://localhost:8000/")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 测试聊天端点 - 教育请求
    print("\n测试聊天端点 - 教育请求...")
    edu_request = {
        "content": "我想学习数学",
        "user_id": "test_user_1"
    }
    response = requests.post(
        "http://localhost:8000/api/chat",
        json=edu_request
    )
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 测试聊天端点 - 安全请求
    print("\n测试聊天端点 - 安全请求...")
    safety_request = {
        "content": "安全检查相关内容",
        "user_id": "test_user_2"
    }
    response = requests.post(
        "http://localhost:8000/api/chat",
        json=safety_request
    )
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 测试教育问答端点
    print("\n测试教育问答端点...")
    edu_ask_request = {
        "content": "什么是语文？",
        "user_id": "test_user_3"
    }
    response = requests.post(
        "http://localhost:8000/api/edu/ask",
        json=edu_ask_request
    )
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")

if __name__ == "__main__":
    test_api()