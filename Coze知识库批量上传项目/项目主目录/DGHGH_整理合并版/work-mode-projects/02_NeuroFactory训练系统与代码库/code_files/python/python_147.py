# 模拟 AnythingLLM 集成接口
class AnythingLLMInterface:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def generate(self, prompt, context=None):
        # 调用外部 LLM 服务
        return f"响应（基于提示：{prompt[:50]}...）"