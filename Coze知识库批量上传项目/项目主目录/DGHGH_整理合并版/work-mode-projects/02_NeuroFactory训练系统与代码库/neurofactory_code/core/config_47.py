from runtime import Args
from typings.get_video_text.get_video_text import Input, Output
import re
import requests

# ---------- 配置 ----------
# 推荐使用 阿里云百炼 SenseVoice 或 火山引擎 ASR
# 此处提供模拟版 + 可接入的真实 API 框架
ASR_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"  # 示例
ASR_API_KEY = "{{secrets.ASR_API_KEY}}"

def get_video_info(video_url: str) -> dict:
    """通过第三方 API 获取视频信息及文案"""
    # 1. 提取视频 ID
    video_id_match = re.search(r'/video/(\d+)', video_url)
    if not video_id_match:
        return {"title": "", "transcript": "", "status": "error: invalid video url"}
    video_id = video_id_match.group(1)
    
    # 2. 使用 TikHub 获取视频元数据（包括标题）
    # 注意：免费调用可能受限，生产环境建议申请正式 key
    tikhub_key = "{{secrets.TIKHUB_API_KEY}}"
    if tikhub_key and not tikhub_key.startswith("{{"):
        headers = {"Authorization": f"Bearer {tikhub_key}"}
        try:
            resp = requests.get(
                f"https://api.tikhub.io/api/v1/douyin/app/v3/fetch_one_video_by_video_id",
                headers=headers,
                params={"video_id": video_id},
                timeout=10
            )
            data = resp.json()
            title = data.get("data", {}).get("aweme_detail", {}).get("desc", "")
            # 获取视频播放地址（用于 ASR）
            video_play_url = data.get("data", {}).get("aweme_detail", {}).get("video", {}).get("play_addr", {}).get("url_list", [""])[0]
        except Exception:
            title = f"抖音视频 {video_id}"
            video_play_url = ""
    else:
        title = f"抖音视频 {video_id}"
        video_play_url = ""
    
    # 3. 获取字幕或进行语音识别
    transcript = ""
    # 方案A：如果有现成字幕（抖音部分视频有 OCR 字幕）
    # 方案B：调用 ASR 服务
    if ASR_API_KEY and not ASR_API_KEY.startswith("{{") and video_play_url:
        # 调用阿里云百炼语音识别（示例）
        headers = {
            "Authorization": f"Bearer {ASR_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "paraformer-v2",
            "input": {"file_urls": [video_play_url]},
            "parameters": {"language": "zh"}
        }
        try:
            resp = requests.post(ASR_API_URL, headers=headers, json=payload, timeout=30)
            result = resp.json()
            transcript = result.get("output", {}).get("sentences", [{}])[0].get("text", "")
        except Exception:
            transcript = ""
    
    # 降级方案：返回模拟文案（演示用，实际请替换为真实识别）
    if not transcript:
        transcript = f"【模拟文案】这是视频 {video_id} 的口播内容演示。实际使用请配置 ASR_API_KEY 或使用其他语音识别服务。"
    
    return {
        "title": title,
        "transcript": transcript,
        "status": "success" if title else "partial"
    }

def handler(args: Args[Input]) -> Output:
    inp = args.input
    video_url = getattr(inp, 'video_url', None)
    if not video_url:
        return Output(title="", transcript="", status="error: missing video_url")
    
    result = get_video_info(video_url)
    return Output(
        title=result["title"],
        transcript=result["transcript"],
        status=result["status"]
    )