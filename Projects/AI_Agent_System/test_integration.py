import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time
import socket

app = Flask(__name__)

deepseek_api_key = "YOUR_DEEPSEEK_API_KEY"
deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"

@app.route('/')
def index():
    return jsonify({
        "status": "running",
        "services": ["deepseek", "coze", "360browser"],
        "time": datetime.now().isoformat()
    })

@app.route('/api/deepseek', methods=['POST'])
def deepseek_api():
    try:
        data = request.json
        response = deepseek_chat(data['messages'])
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def deepseek_chat(messages):
    """调用DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {deepseek_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.3
    }
    response = requests.post(deepseek_api_url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

def run_server():
    """运行服务器"""
    app.run(host='0.0.0.0', port=5000, debug=False)

def check_service():
    """检查服务状态"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        return result == 0
    except:
        return False

if __name__ == "__main__":
    print("测试集成服务...")
    
    # 启动服务器线程
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    print("服务器启动中...")
    time.sleep(3)
    
    if check_service():
        print("✅ 服务器运行正常")
        
        # 测试DeepSeek API
        try:
            test_messages = [{"role": "user", "content": "测试连接"}]
            response = deepseek_chat(test_messages)
            print("✅ DeepSeek API 连接成功")
            print(f"回复: {response['choices'][0]['message']['content'][:50]}...")
        except Exception as e:
            print(f"❌ DeepSeek API 错误: {str(e)}")
    else:
        print("❌ 服务器启动失败")
    
    print("测试完成")