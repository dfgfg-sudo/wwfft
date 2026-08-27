import asyncio
import json
import os
import re
import subprocess
import time
from pathlib import Path
import whisper
from playwright.async_api import async_playwright
from tqdm import tqdm

# =================== OpenClaw 配置 ===================
CONFIG = {
    "bloggers": [
        {"name": "OpenClaw（执行力）", "url": "https://www.douyin.com/user/实际ID"},
        {"name": "Hermes（学习力）",   "url": "https://www.douyin.com/user/实际ID"}
    ],
    "max_videos_per_blogger": 0,          # 0=全部
    "download_dir": "./video_cache",
    "output_kb": "hermes_knowledge.jsonl",
    "whisper_model": "small",             # tiny/base/small/medium/large
    "cookie_source": "chrome",            # None或"cookies.txt"
    "delete_video_after_process": True    # 节省空间
}
# ===================================================

def safe_filename(s):
    return re.sub(r'[\\/*?:"<>|]', '_', s)[:80]

async def fetch_all_video_urls(homepage_url, max_count):
    """OpenClaw核心能力：用手机浏览器模拟，采集所有视频链接"""
    links = set()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)  # 观察运行可改True
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0) AppleWebKit/605.1.15"
        )
        page = await context.new_page()
        await page.goto(homepage_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)

        last_scroll = 0
        while True:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2500)

            elems = await page.query_selector_all('a[href*="/video/"]')
            for e in elems:
                href = await e.get_attribute("href")
                if href:
                    full = "https://www.douyin.com" + href.split("?")[0]
                    links.add(full)

            current_scroll = await page.evaluate("document.body.scrollHeight")
            if current_scroll == last_scroll or (max_count and len(links) >= max_count):
                break
            last_scroll = current_scroll

        await browser.close()
    return list(links)[:max_count] if max_count else list(links)

def download_video(url, save_folder):
    """OpenClaw执行下载，复用登录态"""
    os.makedirs(save_folder, exist_ok=True)
    cmd = [
        "yt-dlp", "--no-playlist",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "-o", f"{save_folder}/%(title).80s_%(id)s.%(ext)s",
        url
    ]
    if CONFIG["cookie_source"] == "chrome":
        cmd += ["--cookies-from-browser", "chrome"]
    elif CONFIG["cookie_source"] and Path(CONFIG["cookie_source"]).exists():
        cmd += ["--cookies", CONFIG["cookie_source"]]

    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        files = sorted(Path(save_folder).glob("*.mp4"), key=os.path.getmtime, reverse=True)
        return str(files[0]) if files else None
    except:
        return None

def transcribe_speech(video_path, model):
    """OpenClaw调用Whisper，返回完整口播文字"""
    result = model.transcribe(video_path, language="zh", verbose=False)
    return result["text"].strip()

def execute_blogger_extraction(blogger):
    """OpenClaw单博主全流程：链接→下载→转写→清洗"""
    name = blogger["name"]
    url = blogger["url"]
    print(f"\n🚀 OpenClaw启动：正在处理博主 【{name}】")
    links = asyncio.run(fetch_all_video_urls(url, CONFIG["max_videos_per_blogger"]))
    if not links:
        print("❌ 未获取到视频链接，请确认主页URL和Cookie有效性。")
        return []

    print(f"📊 共发现 {len(links)} 个视频，开始批量下载与转写...")
    model = whisper.load_model(CONFIG["whisper_model"])
    result_items = []

    for idx, video_url in enumerate(tqdm(links, desc=name), 1):
        video_file = download_video(video_url, CONFIG["download_dir"])
        if not video_file:
            continue
        try:
            full_text = transcribe_speech(video_file, model)
        except:
            full_text = ""

        title = Path(video_file)您这个描述，已经不只是“提取文案”的技术问题，而是一个完整的AI个人知识体系构建方案。我完全理解您想要的终极形态：
“OpenClaw（执行）”负责流程自动化，“Hermes（学习）”负责知识内化与问答，两者结合，打造专属于你的博主智慧库。

下面我给出完整实现方案，且将“OpenClaw”与“Hermes”从单纯的博主名字，升级为你系统架构的两个核心AI角色。

---

一、系统总览：双核AI工作流