from runtime import Args
from typings.query.query import Input, Output
import json
import requests

COZE_API_TOKEN = "{{secrets.COZE_API_TOKEN}}"
# 建议使用 Coze 工作流中的 Bot ID 进行 RAG 问答，也可以直接调用知识库检索 API
# 此处实现一个简单的知识库检索 + 大模型生成（需要配置工作流，更推荐在智能体中调用此工具）
# 为简化，我们调用 Coze 的对话接口，并指定知识库
COZE_BOT_ID = "{{secrets.COZE_BOT_ID}}"  # 在 Coze 中创建一个 Bot，关联该知识库

def handler(args: Args[Input]) -> Output:
    inp = args.input
    kb_id = getattr(inp, 'knowledge_base_id', None)
    question = getattr(inp, 'question', None)
    top_k = getattr(inp, 'top_k', 5)
    
    if not kb_id or not question:
        return Output(answer="", sources="[]", status="error: missing parameters")
    if not COZE_API_TOKEN or COZE_API_TOKEN.startswith("{{"):
        return Output(answer="", sources="[]", status="error: COZE_API_TOKEN not configured")
    
    # 方案1：如果有配置 Bot，使用 Bot 对话
    if COZE_BOT_ID and not COZE_BOT_ID.startswith("{{"):
        headers = {
            "Authorization": f"Bearer {COZE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "bot_id": COZE_BOT_ID,
            "user_id": "hermes_user",
            "additional_messages": [{"role": "user", "content": question, "content_type": "text"}],
            "knowledge_base_ids": [kb_id],
            "auto_save": True
        }
        try:
            resp = requests.post("https://api.coze.cn/v1/chat", headers=headers, json=payload, timeout=60)
            data = resp.json()
            answer = ""
            sources = []
            if "messages" in data:
                for msg in data["messages"]:
                    if msg.get("role") == "assistant":
                        answer = msg.get("content", "")
                        if "knowledge" in msg:
                            for ref in msg["knowledge"]:
                                sources.append(ref.get("title", ""))
            return Output(answer=answer, sources=json.dumps(sources, ensure_ascii=False), status="success")
        except Exception as e:
            return Output(answer="", sources="[]", status=f"error: {str(e)}")
    
    # 方案2：直接调用知识库检索 API（不带生成）
    # 注意：Coze 知识库检索接口需要额外配置，建议优先使用 Bot 方式
    return Output(
        answer="请先配置 COZE_BOT_ID，或在 Coze 智能体中直接引用此知识库进行对话。",
        sources="[]",
        status="config_missing"
    )