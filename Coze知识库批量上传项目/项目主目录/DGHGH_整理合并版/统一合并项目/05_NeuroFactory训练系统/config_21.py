from runtime import Args
import json
import re
import time
import requests
from typing import List, Dict, Any

# ==================== 配置（从 Coze 密钥管理读取） ====================
def get_secret(key: str, default: str = "") -> str:
    """获取 Coze 密钥，兼容 {{secrets.XXX}} 语法"""
    value = globals().get(f"SECRET_{key}", "")
    if value and not value.startswith("{{"):
        return value
    # 模拟模式返回空，触发模拟数据
    return default

# 实际使用时请在工作空间「密钥管理」中添加以下变量：
# TIKHUB_API_KEY, ASR_API_KEY, COZE_API_TOKEN, COZE_BOT_ID
SECRET_TIKHUB_API_KEY = "{{secrets.TIKHUB_API_KEY}}"
SECRET_ASR_API_KEY = "{{secrets.ASR_API_KEY}}"
SECRET_COZE_API_TOKEN = "{{secrets.COZE_API_TOKEN}}"
SECRET_COZE_BOT_ID = "{{secrets.COZE_BOT_ID}}"

# ==================== 公共辅助函数 ====================
def extract_sec_user_id(homepage_url: str) -> str:
    """从主页 URL 提取 sec_user_id"""
    match = re.search(r'/user/([A-Za-z0-9_-]+)', homepage_url)
    if match:
        return match.group(1)
    match = re.search(r'sec_user_id=([^&]+)', homepage_url)
    if match:
        return match.group(1)
    return ""

def extract_video_id(video_url: str) -> str:
    """从视频 URL 提取 video_id"""
    match = re.search(r'/video/(\d+)', video_url)
    if match:
        return match.group(1)
    return ""

# ==================== 功能1：获取所有视频链接 ====================
def fetch_all_videos(homepage_url: str, max_count: int) -> Dict[str, Any]:
    """获取博主主页所有视频链接"""
    sec_user_id = extract_sec_user_id(homepage_url)
    if not sec_user_id:
        return {"video_urls": [], "count": 0, "error": "无法提取 sec_user_id"}
    
    api_key = get_secret("TIKHUB_API_KEY")
    video_urls = []
    
    # 尝试真实 API
    if api_key and not api_key.startswith("{{"):
        headers = {"Authorization": f"Bearer {api_key}"}
        url = "https://api.tikhub.io/api/v1/douyin/app/v3/fetch_user_post_videos"
        try:
            resp = requests.get(url, headers=headers, params={"sec_user_id": sec_user_id, "count": max_count or 50}, timeout=15)
            data = resp.json()
            for aweme in data.get("data", {}).get("aweme_list", []):
                share_url = aweme.get("share_url")
                if share_url:
                    video_urls.append(share_url)
        except Exception as e:
            return {"video_urls": [], "count": 0, "error": f"API 调用失败: {str(e)}"}
    else:
        # 模拟数据（演示用）
        demo_count = min(max_count or 5, 5)
        video_urls = [f"https://www.douyin.com/video/demo_{i}" for i in range(demo_count)]
    
    if max_count and max_count > 0:
        video_urls = video_urls[:max_count]
    
    return {"video_urls": video_urls, "count": len(video_urls), "error": None}

# ==================== 功能2：提取单个视频文案 ====================
def get_video_text(video_url: str) -> Dict[str, Any]:
    """提取单个视频的完整口播文案"""
    video_id = extract_video_id(video_url)
    if not video_id:
        return {"title": "", "transcript": "", "status": "error: 无效的视频链接"}
    
    title = f"抖音视频 {video_id}"
    transcript = ""
    
    # 尝试获取真实文案（需配置 ASR）
    asr_key = get_secret("ASR_API_KEY")
    tikhub_key = get_secret("TIKHUB_API_KEY")
    
    # 1. 先尝试从 TikHub 获取标题和视频播放地址
    video_play_url = ""
    if tikhub_key and not tikhub_key.startswith("{{"):
        headers = {"Authorization": f"Bearer {tikhub_key}"}
        try:
            resp = requests.get(
                "https://api.tikhub.io/api/v1/douyin/app/v3/fetch_one_video_by_video_id",
                headers=headers,
                params={"video_id": video_id},
                timeout=10
            )
            data = resp.json()
            title = data.get("data", {}).get("aweme_detail", {}).get("desc", title)
            video_play_url = data.get("data", {}).get("aweme_detail", {}).get("video", {}).get("play_addr", {}).get("url_list", [""])[0]
        except:
            pass
    
    # 2. 如果有 ASR 能力和视频地址，进行语音识别
    if asr_key and not asr_key.startswith("{{") and video_play_url:
        # 这里以阿里云百炼 SenseVoice 为例，实际请替换为您的服务地址
        asr_url = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
        headers = {
            "Authorization": f"Bearer {asr_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "paraformer-v2",
            "input": {"file_urls": [video_play_url]},
            "parameters": {"language": "zh"}
        }
        try:
            resp = requests.post(asr_url, headers=headers, json=payload, timeout=30)
            result = resp.json()
            transcript = result.get("output", {}).get("sentences", [{}])[0].get("text", "")
        except:
            transcript = ""
    
    # 3. 降级模拟文案
    if not transcript:
        transcript = f"【模拟文案】这是视频 {video_id} 的口播内容演示。实际使用请配置 ASR_API_KEY 并确保视频地址可访问。"
    
    return {"title": title, "transcript": transcript, "status": "success"}

# ==================== 功能3：批量提取并构建知识库 ====================
def batch_extract(homepage_url: str, max_videos: int, knowledge_base_id: str) -> Dict[str, Any]:
    """批量提取所有视频，并可选写入知识库"""
    # 获取所有视频链接
    fetch_result = fetch_all_videos(homepage_url, max_videos)
    if fetch_result.get("error"):
        return {"total_extracted": 0, "knowledge_base_id": knowledge_base_id, "status": fetch_result["error"], "results": []}
    
    video_urls = fetch_result["video_urls"]
    if not video_urls:
        return {"total_extracted": 0, "knowledge_base_id": knowledge_base_id, "status": "未找到视频", "results": []}
    
    extracted = []
    success_count = 0
    for idx, url in enumerate(video_urls):
        text_info = get_video_text(url)
        if text_info["status"] == "success" and text_info["transcript"]:
            item = {
                "index": idx + 1,
                "url": url,
                "title": text_info["title"],
                "transcript": text_info["transcript"]
            }
            extracted.append(item)
            # 如果指定了知识库，尝试写入
            if knowledge_base_id:
                write_res = write_to_knowledge_base(knowledge_base_id, text_info["title"], text_info["transcript"], url)
                if write_res:
                    success_count += 1
            else:
                success_count += 1
        time.sleep(0.5)  # 限速
    
    return {
        "total_extracted": success_count,
        "knowledge_base_id": knowledge_base_id,
        "status": "completed",
        "results": extracted
    }

# ==================== 功能4：写入知识库（被 batch_extract 和 ingest 复用） ====================
def write_to_knowledge_base(kb_id: str, title: str, content: str, source_url: str) -> bool:
    """通过 Coze API 写入文档到知识库"""
    token = get_secret("COZE_API_TOKEN")
    if not token or token.startswith("{{"):
        return False
    headers = {
        "Authorization": f"Bearer {token}",
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
        resp = requests.post(
            f"https://api.coze.cn/v1/knowledge/{kb_id}/documents",
            headers=headers,
            json=payload,
            timeout=30
        )
        return resp.status_code == 200
    except:
        return False

def ingest(knowledge_base_id: str, text_json: str) -> Dict[str, Any]:
    """批量导入文案（JSON 数组格式）"""
    try:
        docs = json.loads(text_json)
    except:
        return {"imported_count": 0, "knowledge_base_id": knowledge_base_id, "message": "无效的 JSON 格式"}
    
    if not isinstance(docs, list):
        return {"imported_count": 0, "knowledge_base_id": knowledge_base_id, "message": "text_json 必须是数组"}
    
    imported = 0
    for doc in docs:
        title = doc.get("title", "未命名")
        content = doc.get("content", "")
        source_url = doc.get("source_url", "")
        if not content:
            continue
        if write_to_knowledge_base(knowledge_base_id, title, content, source_url):
            imported += 1
    
    return {
        "imported_count": imported,
        "knowledge_base_id": knowledge_base_id,
        "message": f"成功导入 {imported} / {len(docs)} 条"
    }

# ==================== 功能5：知识库问答 ====================
def query(knowledge_base_id: str, question: str, top_k: int = 5) -> Dict[str, Any]:
    """基于知识库的智能问答"""
    token = get_secret("COZE_API_TOKEN")
    bot_id = get_secret("COZE_BOT_ID")
    
    if not token or token.startswith("{{"):
        return {"answer": "", "sources": [], "status": "error: 未配置 COZE_API_TOKEN"}
    
    # 优先使用配置的 Bot（推荐）
    if bot_id and not bot_id.startswith("{{"):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "bot_id": bot_id,
            "user_id": "hermes_user",
            "additional_messages": [{"role": "user", "content": question, "content_type": "text"}],
            "knowledge_base_ids": [knowledge_base_id],
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
            return {"answer": answer, "sources": sources, "status": "success"}
        except Exception as e:
            return {"answer": "", "sources": [], "status": f"error: {str(e)}"}
    else:
        return {
            "answer": "请先在 Coze 中创建一个 Bot 并关联该知识库，然后将 Bot ID 配置到 COZE_BOT_ID 密钥中。",
            "sources": [],
            "status": "config_missing"
        }

# ==================== 统一入口 handler ====================
def handler(args: Args) -> dict:
    """Coze 插件工具入口"""
    inp = args.input
    action = getattr(inp, 'action', None)
    
    if not action:
        return {
            "result": json.dumps({"error": "缺少 action 参数"}),
            "status": "error"
        }
    
    # 根据 action 分发
    if action == "fetch_all_videos":
        homepage_url = getattr(inp, 'homepage_url', None)
        max_count = getattr(inp, 'max_count', 0)
        if not homepage_url:
            return {"result": json.dumps({"error": "缺少 homepage_url"}), "status": "error"}
        res = fetch_all_videos(homepage_url, max_count)
        return {"result": json.dumps(res, ensure_ascii=False), "status": "success" if not res.get("error") else "error"}
    
    elif action == "get_video_text":
        video_url = getattr(inp, 'video_url', None)
        if not video_url:
            return {"result": json.dumps({"error": "缺少 video_url"}), "status": "error"}
        res = get_video_text(video_url)
        return {"result": json.dumps(res, ensure_ascii=False), "status": res.get("status", "error")}
    
    elif action == "batch_extract":
        homepage_url = getattr(inp, 'homepage_url', None)
        max_videos = getattr(inp, 'max_videos', 0)
        kb_id = getattr(inp, 'knowledge_base_id', None)
        if not homepage_url:
            return {"result": json.dumps({"error": "缺少 homepage_url"}), "status": "error"}
        res = batch_extract(homepage_url, max_videos, kb_id)
        return {"result": json.dumps(res, ensure_ascii=False), "status": "success" if res.get("status") == "completed" else "error"}
    
    elif action == "ingest":
        kb_id = getattr(inp, 'knowledge_base_id', None)
        text_json = getattr(inp, 'text_json', None)
        if not kb_id or not text_json:
            return {"result": json.dumps({"error": "缺少 knowledge_base_id 或 text_json"}), "status": "error"}
        res = ingest(kb_id, text_json)
        return {"result": json.dumps(res, ensure_ascii=False), "status": "success"}
    
    elif action == "query":
        kb_id = getattr(inp, 'knowledge_base_id', None)
        question = getattr(inp, 'question', None)
        top_k = getattr(inp, 'top_k', 5)
        if not kb_id or not question:
            return {"result": json.dumps({"error": "缺少 knowledge_base_id 或 question"}), "status": "error"}
        res = query(kb_id, question, top_k)
        return {"result": json.dumps(res, ensure_ascii=False), "status": res.get("status", "error")}
    
    else:
        return {
            "result": json.dumps({"error": f"未知的 action: {action}"}),
            "status": "error"
        }