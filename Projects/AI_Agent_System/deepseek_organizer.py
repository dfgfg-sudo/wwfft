import requests
from datetime import datetime

def organize_deepseek_chat(content, api_key):
    """使用DeepSeek API整理聊天内容"""
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
                "content": "You are a professional content organizer specializing in AI agent systems. Please organize the following content about '小龙虾' (AI software agents) into a clear, structured format. Focus on security, free usage, zero token consumption, and integration with Trae software. Remove any irrelevant information, organize by topics, and present it in a logical order."
            },
            {
                "role": "user",
                "content": f"Please organize the following content about '小龙虾' (AI software agents):\n\n{content}"
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

def save_organized_content(content, source_url):
    """保存整理后的内容"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"d:\\Projects\\AI_Agent_System\\organized_crayfish_agents_{timestamp}.md"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 小龙虾（AI软件智能体）完全安全指南\n\n")
            f.write(f"Source: {source_url}\n\n")
            f.write(f"Organized on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(content)
        return output_file
    except Exception as e:
        return f"Error saving file: {str(e)}"

def main():
    """主函数"""
    print("小龙虾（AI软件智能体）内容整理工具")
    print("=" * 60)
    print("This tool helps you organize content about '小龙虾' AI agents")
    print("=" * 60)
    
    # 输入信息
    api_key = "YOUR_DEEPSEEK_API_KEY"  # 用户提供的API密钥
    source_url = "User provided content"
    
    print(f"Using DeepSeek API key: {api_key[:8]}...")
    print("\n1. Processing content...")
    
    # 直接使用用户提供的内容
    content = """基于海外开源项目推出大量本土化版本的AI软件智能体（俗称“小龙虾”）更多全部完整的全部更多版本和更多类型的和完整更多符合安全使用免费版本平台的 和符合全部安全使用的 还有完全安全免费使用的 安全自动化操作使用的 还有更多小龙虾安全运行版本的和安全调用版本和符合非常安全的外部势力软件里面集成调用自动化操作符合安全自动化使用的 和完整全部不消耗任何流量的和完整全部符合安全正确使用完全免费使用的模型的 符合非常安全Token算力消耗完全为零的 同时速度运行安全块符合我自己的Trae字节软件的"""
    
    print("2. Organizing content...")
    
    # 整理内容
    organized_content = organize_deepseek_chat(content, api_key)
    
    if "Error" in organized_content:
        print(f"Error: {organized_content}")
        return
    
    print("3. Saving organized content...")
    
    # 保存整理后的内容
    output_file = save_organized_content(organized_content, source_url)
    
    if "Error" in output_file:
        print(f"Error: {output_file}")
        return
    
    print(f"\n✅ Task completed successfully!")
    print(f"Organized content saved to: {output_file}")
    print("\nContent preview:")
    print("=" * 50)
    print(organized_content[:500] + "..." if len(organized_content) > 500 else organized_content)
    print("=" * 50)

if __name__ == "__main__":
    main()