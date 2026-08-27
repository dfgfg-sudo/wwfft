from runtime import Args
from typings.query.query import Input, Output
import json
import requests

COZE_API_TOKEN = "{{secrets.COZE_API_TOKEN}}"
COZE_BOT_ID = "{{secrets.COZE_BOT_ID}}"

def handler(args: Args[Input]) -> Output:
    inp = args.input
    kb_id = getattr(inp, 'knowledge_base_id', None)
    question = getattr(inp, 'question', None)
    top_k = getattr(inp, 'top_k', 5)
    if not kb_id or not question:
        return Output(answer="", sources="[]", status="error: missing parameters")
    if not COZE_API_TOKEN or COZE_API_TOKEN.startswith("{{"):
        return Output(answer="", sources="[]", status="error: COZE_API_TOKEN not configured")
    if COZE_BOT_ID and not COZE_BOT_ID.startswith("{{"):
        headers = {"Authorization": f"Bearer {COZE_API_TOKEN}", "Content-Type": "application/json"}
        payload = {"bot_id": COZE_BOT_ID, "user_id": "hermes_user", "additional_messages": [{"role": "user", "content": question, "content_type": "text"}], "knowledge_base_ids": [kb_id], "auto_save": True}
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
    return Output(answer="请配置 COZE_BOT_ID，或在 Coze 智能体中直接引用知识库。", sources="[]", status="config_missing")