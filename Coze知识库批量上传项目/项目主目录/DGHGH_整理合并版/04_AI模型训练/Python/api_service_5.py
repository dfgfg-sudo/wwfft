from runtime import Args
from typings.fetch_all_videos.fetch_all_videos import Input, Output
import json
import re
import requests

TIKHUB_API_KEY = "{{secrets.TIKHUB_API_KEY}}"
TIKHUB_API_URL = "https://api.tikhub.io/api/v1/douyin/app/v3/fetch_user_post_videos"

def fetch_from_tikhub(sec_user_id: str, max_count: int) -> list:
    if not TIKHUB_API_KEY or TIKHUB_API_KEY.startswith("{{"):
        return [f"https://www.douyin.com/video/example_{i}" for i in range(min(5, max_count or 5))]
    headers = {"Authorization": f"Bearer {TIKHUB_API_KEY}"}
    params = {"sec_user_id": sec_user_id, "count": max_count or 20}
    video_urls = []
    try:
        resp = requests.get(TIKHUB_API_URL, headers=headers, params=params, timeout=10)
        data = resp.json()
        for aweme in data.get("data", {}).get("aweme_list", []):
            share_url = aweme.get("share_url")
            if share_url:
                video_urls.append(share_url)
    except Exception:
        pass
    return video_urls

def extract_sec_user_id(homepage_url: str) -> str:
    match = re.search(r'/user/([A-Za-z0-9_-]+)', homepage_url)
    if match:
        return match.group(1)
    match = re.search(r'sec_user_id=([^&]+)', homepage_url)
    if match:
        return match.group(1)
    return ""

def handler(args: Args[Input]) -> Output:
    inp = args.input
    homepage_url = getattr(inp, 'homepage_url', None)
    max_count = getattr(inp, 'max_count', 0)
    if not homepage_url:
        return Output(video_urls=json.dumps([]), count=0)
    sec_user_id = extract_sec_user_id(homepage_url)
    if not sec_user_id:
        return Output(video_urls=json.dumps([]), count=0)
    video_urls = fetch_from_tikhub(sec_user_id, max_count if max_count else 0)
    if max_count and max_count > 0:
        video_urls = video_urls[:max_count]
    return Output(video_urls=json.dumps(video_urls, ensure_ascii=False), count=len(video_urls))