from runtime import Args
from typings.get_video_text.get_video_text import Input, Output
import json
import re
import requests

def get_video_info(video_url: str) -> dict:
    """
    使用外部API获取视频详情和文案
    推荐方案：
    1. TikHub API + 阿里云百炼ASR（语音识别）
    2. Coze已有插件“抖音文案获取”
    """
    # 确保视频链接格式正确
    if not video_url.startswith("http"):
        video_url = "https://" + video_url
    
    # 配置TikHub API Key（可从Coze的secret变量获取）
    API_KEY = "your_api_key_here"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # 获取视频详情
        response = requests.get(
            f"https://api.tikhub.io/api/v1/douyin/app/v3/fetch_one_video_by_share_url",
            headers=headers,
            params={"share_url": video_url},
            timeout=15
        )
        response.raise_for_status()
        
        data = response.json().get("data", {})
        aweme_detail = data.get("aweme_detail", {})
        
        title = aweme_detail.get("desc", "")
        video_play_url = aweme_detail.get("video", {}).get("play_addr", {}).get("url_list", [""])[0]
        
        # 语音识别获取文案，可使用Coze内置ASR或外部服务
        transcript = ""  # 实际调用ASR服务
        # 方案1: 使用阿里云百炼SenseVoice
        # transcript = asr_service.transcribe(video_play_url)
        # 方案2: 调用Coze已有的“字幕提取插件”
        
        return {
            "title": title,
            "transcript": transcript,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "title": "",
            "transcript": "",
            "status": f"error: {str(e)}"
        }

def handler(args: Args[Input]) -> Output:
    input_data = args.input
    video_url = getattr(input_data, 'video_url', None)
    
    if not video_url:
        return Output(title="", transcript="", status="error: missing video_url")
    
    result = get_video_info(video_url)
    return Output(
        title=result["title"],
        transcript=result["transcript"],
        status=result["status"]
    )