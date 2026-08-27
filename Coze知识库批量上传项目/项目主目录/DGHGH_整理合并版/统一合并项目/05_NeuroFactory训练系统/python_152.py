# 扩展语言检测功能
import langdetect

def enhanced_language_detection(text: str) -> str:
    """增强语言检测"""
    try:
        from langdetect import detect
        return detect(text)
    except:
        return "未知"