import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time

class IntegratedService:
    def __init__(self):
        # 加载配置文件
        self.config = self.load_config()
        self.deepseek_api_key = self.config['deepseek']['api_key']
        self.deepseek_api_url = self.config['deepseek']['api_url']
        self.coze_api_key = self.config['coze']['api_key']
        self.coze_api_url = self.config['coze']['api_url']
        self.host = self.config['server']['host']
        self.port = self.config['server']['port']
        self.app = Flask(__name__)
        self.setup_routes()
        self.skills = self.load_skills()
    
    def load_config(self):
        """加载配置文件"""
        config_path = "d:\\Projects\\AI_Agent_System\\config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            return {
                "deepseek": {
                    "api_key": "YOUR_DEEPSEEK_API_KEY",
                    "api_url": "https://api.deepseek.com/v1/chat/completions"
                },
                "coze": {
                    "api_key": "YOUR_COZE_API_KEY",
                    "api_url": "https://api.coze.com/v1/chat"
                },
                "server": {
                    "host": "0.0.0.0",
                    "port": 5000
                },
                "feishu": {
                    "webhook": "/api/feishu/webhook"
                },
                "security": {
                    "enabled": True,
                    "scan": True,
                    "isolation": True
                }
            }
        
    def load_skills(self):
        """加载技能列表"""
        skills = [
            "Cost Optimisation",
            "agent-browser-summarize",
            "all-in-one-assistant",
            "awesome-openclaw-skills",
            "awesome-openclaw-usecases",
            "baidu-web-search",
            "browser-use",
            "capability-evolver",
            "claw-compact",
            "claw-compactor",
            "clawhub",
            "clawsec",
            "code-simplifier",
            "coze-ecosystem-integration",
            "coze-interface-designer",
            "coze-resource-exporter",
            "coze_complete_integration",
            "document-skills",
            "dont-hack-me",
            "exa-search",
            "find-skills",
            "frontend-design",
            "gitclaw",
            "github-skills",
            "jina-reader",
            "lobster-workflow-shell",
            "memory-optimizer",
            "mini-claw",
            "netease-youdao-lobsterai",
            "openclaw-ansible",
            "paddleocr-text-recognition",
            "proactive-agent",
            "prompt-guard",
            "prompt-optimizer",
            "qmd-local-knowledge-base",
            "self-improving-agent",
            "skill-creator",
            "skill-vetter",
            "supermemory",
            "tavily-search-news-aggregator",
            "vercel-agent-skills",
            "video-content-creator",
            "volcengine-arkclaw",
            "x-research-skill",
            "zeroclaw",
            "zhipu-auto-claw"
        ]
        return skills
    
    def setup_routes(self):
        """设置Flask路由"""
        @self.app.route('/')
        def index():
            return jsonify({
                "status": "running",
                "services": ["deepseek", "coze", "360browser"],
                "skills": len(self.skills),
                "time": datetime.now().isoformat()
            })
        
        @self.app.route('/api/deepseek', methods=['POST'])
        def deepseek_api():
            try:
                data = request.json
                response = self.deepseek_chat(data['messages'])
                return jsonify(response)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/coze', methods=['POST'])
        def coze_api():
            try:
                data = request.json
                response = self.coze_chat(data['messages'])
                return jsonify(response)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/360browser', methods=['POST'])
        def browser_api():
            try:
                data = request.json
                response = self.browser_action(data['action'], data.get('url'), data.get('query'))
                return jsonify(response)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/feishu/webhook', methods=['POST'])
        def feishu_webhook():
            try:
                data = request.json
                response = self.handle_feishu_message(data)
                return jsonify(response)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def deepseek_chat(self, messages):
        """调用DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.3
        }
        response = requests.post(self.deepseek_api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    
    def coze_chat(self, messages):
        """调用Coze API"""
        headers = {
            "Authorization": f"Bearer {self.coze_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "coze-ai",
            "messages": messages,
            "temperature": 0.3
        }
        response = requests.post(self.coze_api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    
    def browser_action(self, action, url=None, query=None):
        """360安全浏览器功能"""
        if action == "search":
            search_url = f"https://www.so.com/s?q={query}"
            return {"action": "search", "url": search_url, "status": "success"}
        elif action == "browse":
            return {"action": "browse", "url": url, "status": "success"}
        else:
            return {"action": action, "status": "error", "message": "Invalid action"}
    
    def handle_feishu_message(self, data):
        """处理飞书消息"""
        # 解析飞书消息
        message = data.get('message', {}).get('content', '')
        
        # 简单的意图识别
        if 'deepseek' in message.lower():
            # 调用DeepSeek API
            response = self.deepseek_chat([
                {"role": "user", "content": message}
            ])
            return {
                "reply": response['choices'][0]['message']['content'],
                "service": "deepseek"
            }
        elif 'coze' in message.lower():
            # 调用Coze API
            response = self.coze_chat([
                {"role": "user", "content": message}
            ])
            return {
                "reply": response['choices'][0]['message']['content'],
                "service": "coze"
            }
        elif 'browser' in message.lower() or '搜索' in message:
            # 调用浏览器功能
            query = message.replace('browser', '').replace('搜索', '').strip()
            response = self.browser_action('search', query=query)
            return {
                "reply": f"正在搜索: {query}\n结果地址: {response['url']}",
                "service": "360browser"
            }
        else:
            # 默认回复
            return {
                "reply": "您好！我是集成服务助手，可以帮您调用DeepSeek、Coze和360浏览器功能。请在消息中包含服务名称，例如：'deepseek 帮我写一篇文章'",
                "service": "default"
            }
    
    def run(self):
        """启动服务"""
        print(f"集成服务启动中...")
        print(f"服务地址: http://{self.host}:{self.port}")
        print(f"DeepSeek API: 已配置")
        print(f"Coze API: 已配置 {'(需要填写API密钥)' if self.coze_api_key == 'YOUR_COZE_API_KEY' else ''}")
        print(f"360安全浏览器: 已集成")
        print(f"飞书webhook: http://{self.host}:{self.port}/api/feishu/webhook")
        print(f"技能数量: {len(self.skills)}")
        print(f"安全配置: {'已启用' if self.config['security']['enabled'] else '已禁用'}")
        self.app.run(host=self.host, port=self.port, debug=False)

if __name__ == "__main__":
    service = IntegratedService()
    service.run()