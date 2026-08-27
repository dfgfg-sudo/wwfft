import requests
from datetime import datetime

def optimize_content(content, api_key):
    """使用DeepSeek API优化内容"""
    api_url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional content editor and organizer. Please optimize the following content to make it more structured, clear, and professional. Improve formatting, fix any inconsistencies, and enhance the overall readability while preserving all original information."
            },
            {
                "role": "user",
                "content": f"Please optimize the following content:\n\n{content}"
            }
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def save_optimized_content(content):
    """保存优化后的内容"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"d:\\Projects\\AI_Agent_System\\optimized_crayfish_encyclopedia_{timestamp}.md"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 全球\"小龙虾\"（AI软件智能体）完全安全自动化搭建与使用百科全书\n\n")
            f.write(f"Optimized on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(content)
        return output_file
    except Exception as e:
        return f"Error saving file: {str(e)}"

def main():
    """主函数"""
    print("Content Optimizer")
    print("=" * 60)
    print("This tool optimizes content using DeepSeek API")
    print("=" * 60)
    
    # 输入信息
    api_key = "YOUR_DEEPSEEK_API_KEY"  # 用户提供的API密钥
    
    print(f"Using DeepSeek API key: {api_key[:8]}...")
    print("\n1. Processing content...")
    
    # 直接使用用户提供的内容
    content = """龙虾机器人四大类别 《全球"小龙虾"（AI软件智能体）完全安全自动化搭建与使用百科全书》 引言：什么是"小龙虾"？ "小龙虾"是技术圈对基于海外开源项目（主要是OpenClaw）进行本土化二次开发的AI软件智能体的俗称。它们能够模拟人类操作软件、执行自动化任务，并可集成到各类消息平台中。自2025年底OpenClaw项目诞生以来，全球范围内已衍生出数百个版本，形成了庞大的安全自动化生态体系。 本百科全书整合了迄今为止所有关于"小龙虾"的完整信息，涵盖全球版本清单、安全分类、零流量零Token实现方案、外部系统安全集成，以及最重要的——如何在Coze平台和Trae软件中亲手搭建属于自己的、永久免费、完全安全、自动化运行的小龙虾智能体。 第一部分：基础概念与完整分类 1.1 四大核心类别（全景图） 根据早期分类，"龙虾机器人"在中国市场主要分为四大类别，本百科聚焦第一类： 类别 定义 代表案例 本百科覆盖 AI软件智能体（小龙虾） 基于开源项目开发的AI助理，能自动化操作软件 OpenClaw、IronClaw、ArkClaw ✅ 核心覆盖 仿生实体机器人 具身智能机器人，应用于水下/工业场景 卓世科技NextClaw ❌ 不展开 食品工业设备 小龙虾加工自动化设备 睿峰智控剥虾机 ❌ 不展开 死灵机器人学装置 暂无中国应用信息 无 ❌ 无信息 1.2 "小龙虾"的核心特征 所有符合"小龙虾"定义的AI智能体，普遍具备以下特征： 自动化操作：能模拟人类操作软件、执行多步骤任务 可扩展性：通过安装"技能"（Skills）增强功能 多模态交互：支持文本、语音、图像等多种输入 安全沙箱：提供隔离运行环境，保护系统安全 开源基因：绝大多数版本基于OpenClaw等开源项目衍生 第二部分：全球"小龙虾"完整版本百科全书 2.1 核心起源：OpenClaw官方版本 OpenClaw经历了三次更名和持续演进，是"小龙虾"生态的源头： 时间 版本名称 事件 2025年11月 Clawdbot 最初发布，由Peter Steinberger创建 2026年1月27日 Moltbot 首次更名，因Anthropic商标要求 2026年1月30日 OpenClaw 二次更名，完成商标检索和域名保护 OpenClaw官方核心版本（截至2026年3月，主仓库星标