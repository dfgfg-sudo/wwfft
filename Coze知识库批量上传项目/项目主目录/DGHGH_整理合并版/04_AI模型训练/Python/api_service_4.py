from runtime import Args
from typings.query.query import Input, Output
import json
import requests

COZE_API_BASE = "https://api.coze.cn/v1/knowledge"
COZE_BOT_API = "https://api.coze.cn/v1/chat"

def handler(args: Args[Input]) -> Output:
    input_data = args.input
    kb_id = getattr(input_data, 'knowledge_base_id', None)
    question = getattr(input_data, 'question', None)
    top_k = getattr(input_data, 'top_k', 5)
    
    if not kb_id or not question:
        return Output(answer="", sources="[]", status="error: missing parameters")
    
    api_token = "YOUR_API_TOKEN"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # 构建知识库增强的问答请求
    payload = {
        "bot_id": "YOUR_BOT_ID",
        "user_id": "user_hermes",
        "additional_messages": [
            {
                "role": "user",
                "content": question,
                "content_type": "text"
            }
        ],
        "knowledge_base_ids": [kb_id],
        "auto_save": True
    }
    
    try:
        response = requests.post(
            f"{COZE_BOT_API}",
            headers=headers,
            json=payload,
            timeout=60
        )
        result = response.json()
        
        answer = ""
        sources = []
        
        if "messages" in result:
            for msg in result["messages"]:
                if msg.get("role") == "assistant":
                    answer = msg.get("content", "")
                    # 提取引用的知识文档
                    if "knowledge" in msg:
                        for ref in msg.get("knowledge", []):
                            sources.append(ref.get("title", ""))
        
        return Output(
            answer=answer,
            sources=json.dumps(sources, ensure_ascii=False),
            status="success"
        )
        
    except Exception as e:
        return Output(
            answer="",
            sources="[]",
            status=f"error: {str(e)}"
        )