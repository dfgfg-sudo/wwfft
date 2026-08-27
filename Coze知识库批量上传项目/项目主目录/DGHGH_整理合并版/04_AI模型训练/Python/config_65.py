from runtime import Args
from typings.ingest.ingest import Input, Output
import json
import requests

COZE_API_TOKEN = "{{secrets.COZE_API_TOKEN}}"

def handler(args: Args[Input]) -> Output:
    inp = args.input
    kb_id = getattr(inp, 'knowledge_base_id', None)
    text_json = getattr(inp, 'text_json', "[]")
    if not kb_id:
        return Output(imported_count=0, knowledge_base_id="", message="error: missing knowledge_base_id")
    if not COZE_API_TOKEN or COZE_API_TOKEN.startswith("{{"):
        return Output(imported_count=0, knowledge_base_id=kb_id, message="error: COZE_API_TOKEN not configured")
    try:
        docs = json.loads(text_json)
    except:
        return Output(imported_count=0, knowledge_base_id=kb_id, message="error: invalid JSON")
    headers = {"Authorization": f"Bearer {COZE_API_TOKEN}", "Content-Type": "application/json"}
    imported = 0
    for doc in docs:
        title = doc.get("title", "未命名")
        content = doc.get("content", "")
        source_url = doc.get("source_url", "")
        if not content:
            continue
        payload = {"knowledge_base_id": kb_id, "document": {"title": title, "content": content, "source_url": source_url}}
        try:
            resp = requests.post(f"https://api.coze.cn/v1/knowledge/{kb_id}/documents", headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                imported += 1
        except:
            pass
    return Output(imported_count=imported, knowledge_base_id=kb_id, message=f"Successfully imported {imported} of {len(docs)} documents")