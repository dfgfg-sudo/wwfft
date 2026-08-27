import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api"

# 1. 用户注册
def register_user(email, password, name):
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "name": name
    })
    return response.json()

# 2. 用户登录
def login_user(email, password):
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    return response.json()

# 3. 分析需求
def analyze_requirements(description, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/projects/analyze",
        json={"description": description},
        headers=headers
    )
    return response.json()

# 4. 生成项目
def generate_project(project_data, analysis_result, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/projects/generate",
        json={
            "project_data": project_data,
            "analysis_result": analysis_result
        },
        headers=headers
    )
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 注册用户
    register_result = register_user(
        "user@example.com",
        "password123",
        "测试用户"
    )
    print("注册结果:", register_result)
    
    # 登录获取token
    login_result = login_user("user@example.com", "password123")
    token = login_result.get("data", {}).get("token")
    
    if token:
        # 分析需求
        analysis = analyze_requirements(
            "我需要一个博客系统，支持文章发布、分类、评论和用户订阅",
            token
        )
        print("需求分析结果:", analysis)
        
        # 生成项目
        project = generate_project(
            {
                "name": "我的博客系统",
                "description": "一个现代化的博客平台"
            },
            analysis.get("data", {}),
            token
        )
        print("项目生成结果:", project)