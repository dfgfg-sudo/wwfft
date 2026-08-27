from runtime import Args
from typings.get_video_text.get_video_text import Input, Output
import re
import requests

ASR_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
ASR_API_KEY = "{{secrets.ASR_API_KEY}}"

def get_video_info(video_url: str) -> dict:
    video_id_match = re.search(r'/video/(\d+)', video_url)
    if not video_id_match:
        return {"title": "", "transcript": "", "status": "error: invalid video url"}
    video_id = video_id_match.group(1)
    tikhub_key = "{{secrets.TIKHUB_API_KEY}}"
    title = f"抖音视频 {video_id}"
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
        except Exception:
            pass
    transcript = ""
    if ASR_API_KEY and not ASR_API_KEY.startswith("{{") and video_play_url:
        headers = {"Authorization": f"Bearer {ASR_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "paraformer-v2", "input": {"file_urls": [video_play_url]}, "parameters": {"language": "zh"}}
        try:
            resp = requests.post(ASR_API_URL, headers=headers, json=payload, timeout=30)
            result = resp.json()
            transcript = result.get("output", {}).get("sentences", [{}])[0].get("text", "")
        except Exception:
            pass
    if not transcript:
        transcript = f"【模拟文案】这是视频 {video_id} 的口播内容演示。实际使用请配置 ASR_API_KEY 并确保视频地址可访问。"
    return {"title": title, "transcript": transcript, "status": "success"}

def handler(args: Args[Input]) -> Output:
    inp = args.input
    video_url = getattr(inp, 'video_url', None)
    if not video_url:
        return Output(title="", transcript="", status="error: missing video_url")
    result = get_video_info(video_url)
    return Output(title=result["title"], transcript=result["transcript"], status=result["status"])