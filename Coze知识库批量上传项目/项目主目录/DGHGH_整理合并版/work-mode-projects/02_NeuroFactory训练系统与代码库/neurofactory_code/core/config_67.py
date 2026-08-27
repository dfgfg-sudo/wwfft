from runtime import Args
from typings.fetch_all_videos.fetch_all_videos import Input, Output
import json
import re
import requests
import time

def fetch_video_urls_from_api(homepage_url: str, max_count: int) -> list:
    """
    核心逻辑：从抖音主页抓取视频链接
    """
    # 实际实现时需要结合第三方解析API（如TikHub）
    # 这里提供完整接入示例
    video_urls = []
    
    # 提取抖音用户ID
    user_id_match = re.search(r'/user/([0-9a-zA-Z]+)', homepage_url)
    if not user_id_match:
        return []
    
    sec_user_id = user_id_match.group(1)
    
    # 使用TikHub API获取用户视频列表（需配置API Key）
    # headers = {"Authorization": f"Bearer {API_KEY}"}
    # params = {"sec_user_id": sec_user_id, "count": max_count or 20}
    # response = requests.get(API_URL, headers=headers, params=params)
    # data = response.json()
    # for video in data.get("aweme_list", []):
    #     video_urls.append(video.get("share_url") or f"https://www.douyin.com/video/{video.get('aweme_id')}")
    
    # 示例返回
    return video_urls[:max_count] if max_count > 0 else video_urls

def handler(args: Args[Input]) -> Output:
    input_data = args.input
    
    homepage_url = getattr(input_data, 'homepage_url', None)
    max_count = getattr(input_data, 'max_count', 0)
    
    if not homepage_url:
        return Output(video_urls=json.dumps([]), count=0)
    
    video_urls = fetch_video_urls_from_api(homepage_url, max_count)
    
    return Output(
        video_urls=json.dumps(video_urls, ensure_ascii=False),
        count=len(video_urls)
    )