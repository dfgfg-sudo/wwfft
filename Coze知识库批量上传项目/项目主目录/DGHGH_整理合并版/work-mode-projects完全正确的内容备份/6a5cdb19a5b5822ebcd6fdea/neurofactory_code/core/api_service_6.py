from runtime import Args
from typings.ingest.ingest import Input, Output
import json
import requests

COZE_API_BASE = "https://api.coze.cn/v1/knowledge"

def handler(args: Args[Input]) -> Output:
    input_data = args.input
    kb_id = getattr(input_data, 'knowledge_base_id', None)
    text_json = getattr(input_data, 'text_json', "[]")
    metadata = getattr(input_data, 'metadata', "{}")
    
    if not kb_id:
        return Output(imported_count=0, knowledge_base_id="", message="error: missing knowledge_base_id")
    
    try:
        texts = json.loads(text_json)
        metadata_obj = json.loads(metadata) if metadata else {}
    except:
        return Output(imported_count=0, knowledge_base_id=kb_id, message="error: invalid JSON input")
    
    imported = 0
    api_token = metadata_obj.get("api_token", "YOUR_API_TOKEN")
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    for text_item in texts:
        title = text_item.get("title", "video_content")
        content = text_item.get("content", "")
        source_url = text_item.get("source_url", "")
        
        if not content:
            continue
        
        payload = {
            "knowledge_base_id": kb_id,
            "document": {
                "title": title,
                "content": content,
                "source_url": source_url
            }
        }
        
        try:
            response = requests.post(
                f"{COZE_API_BASE}/{kb_id}/documents",
                headers=headers,
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                imported += 1
        except:
            pass
    
    return Output(
        imported_count=imported,
        knowledge_base_id=kb_id,
        message=f"successfully imported {imported} items"
    )