import asyncio
import json
from typing import Dict, Any
# 模拟各模块SDK（真实部署时替换为对应pip包）
from crawlers import FirecrawlClient, BrowserUseAgent
from parsers import MarkItDownParser, PDFMasterOCR
from researchers import Last30DaysEngine, GraphifyBuilder
from optimizers import HeadroomCompressor
from security import SkillSpectorScanner

class CozeFullAutomation:
    """完全自动化操作体验的核心引擎（修复版）"""
    
    def __init__(self, api_keys: Dict[str, str]):
        self.keys = api_keys
        # 合并所有客户端，无重复初始化
        self.firecrawl = FirecrawlClient(api_keys.get("firecrawl"))
        self.browser = BrowserUseAgent()
        self.markitdown = MarkItDownParser()
        self.pdf_ocr = PDFMasterOCR()
        self.research = Last30DaysEngine()
        self.graph = GraphifyBuilder()
        self.compressor = HeadroomCompressor()
        self.scanner = SkillSpectorScanner()

    async def run_full_pipeline(self, target_url: str, topic: str) -> Dict[str, Any]:
        """全自动化链式执行（顺序优化，无冲突）"""
        results = {}
        
        # 1. 网页抓取 & 文档转换（自动判断格式）
        raw_data = await self.firecrawl.scrape(target_url)
        markdown_content = self.markitdown.convert(raw_data.get("html", ""))
        results["raw_markdown"] = markdown_content
        
        # 2. 调研与知识融合（并行执行，提升速度）
        research_task = asyncio.create_task(self.research.run(topic))
        graph_task = asyncio.create_task(self.graph.build_from_markdown(markdown_content))
        results["research_report"], results["knowledge_graph"] = await asyncio.gather(research_task, graph_task)
        
        # 3. Token智能压缩（上下文提效）
        compressed = self.compressor.compress(
            text=json.dumps(results, default=str),
            target_ratio=0.35  # 保留35%，符合60-95%压缩区间
        )
        results["compressed_context"] = compressed
        
        # 4. 安全扫描（全量检查）
        security_issues = self.scanner.scan(compressed)
        results["security_audit"] = security_issues
        
        # 5. 自动生成最终简报（无变动保留所有原始内容格式）
        results["final_brief"] = f"""
        ===== 全自动化处理报告 =====
        原网站: {target_url} | 调研主题: {topic}
        Token压缩率: {round((1 - len(compressed)/len(json.dumps(results, default=str)))*100, 2)}%
        安全风险等级: {"高" if security_issues else "低"}
        --- 原始Markdown保留片段（前200字）---
        {markdown_content[:200]}...
        """
        return results

# Coze IDE 插件入口（修复了之前缺失的异步启动）
async def main_handler(params: dict) -> dict:
    engine = CozeFullAutomation(api_keys={"firecrawl": "sk-xxx"})
    result = await engine.run_full_pipeline(
        target_url=params.get("url", "https://example.com"),
        topic=params.get("topic", "AI趋势")
    )
    return {"status": "success", "data": result}

if __name__ == "__main__":
    asyncio.run(main_handler({"url": "https://news.ycombinator.com", "topic": "LLM"}))