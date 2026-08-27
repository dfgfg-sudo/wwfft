from runtime import Args
from typings.batch_extract.batch_extract import Input, Output
import json
import requests
import time

# Coze知识库写入API配置
COZE_API_BASE = "https://api.coze.cn/v1/knowledge"

def write_to_knowledge_base(kb_id: str, title: str, content: str, source_url: str) -> bool:
    """将提取的文案写入Coze知识库"""
    # 获取授权Token（从Coze环境变量获取）
    api_token = "YOUR_API_TOKEN"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
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
        return response.status_code == 200
    except:
        return False

def batch_extract_videos(homepage_url: str, max_videos: int, kb_id: str) -> dict:
    """
    批量处理全流程：
    1. 获取所有视频链接
    2. 逐个提取文案
    3. 写入知识库
    """
    # 调用工具1获取所有视频链接
    # fetch_result = fetch_all_videos(homepage_url, max_videos)
    # video_urls = json.loads(fetch_result.get("video_urls", "[]"))
    
    video_urls = []  # 示例占位
    total = 0
    
    for idx, video_url in enumerate(video_urls):
        # 调用工具2获取视频文案
        # text_result = get_video_text(video_url)
        title = f"video_{idx+1}"
        transcript = ""
        
        if transcript and kb_id:
            if write_to_knowledge_base(kb_id, title, transcript, video_url):
                total += 1
        
        time.sleep(1)  # 避免请求过快
    
    return {
        "total": total,
        "kb_id": kb_id,
        "status": "completed" if total > 0 else "partial"
    }

def handler(args: Args[Input]) -> Output:
    input_data = args.input
    
    homepage_url = getattr(input_data, 'homepage_url', None)
    max_videos = getattr(input_data, 'max_videos', 0)
    kb_id = getattr(input_data, 'knowledge_base_id', "default_kb_id")
    
    if not homepage_url:
        return Output(total_extracted=0, knowledge_base_id=kb_id, status="error: missing homepage_url")
    
    result = batch_extract_videos(homepage_url, max_videos or 100, kb_id)
    
    return Output(
        total_extracted=result["total"],
        knowledge_base_id=result["kb_id"],
        status=result["status"]
    )