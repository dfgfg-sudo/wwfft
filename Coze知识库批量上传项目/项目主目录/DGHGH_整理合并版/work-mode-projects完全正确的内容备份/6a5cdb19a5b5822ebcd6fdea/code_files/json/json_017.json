{
  "name": "ai-dev-full-toolkit",
  "version": "3.0.0",
  "description": "全自动化AI开发工作流插件（融合抓取/文档/调研/压缩/安全）",
  "author": "Coze-IDE-Integration",
  "permissions": ["network", "filesystem", "env"],
  "tools": [
    { "name": "firecrawl_scrape", "module": "crawlers", "input": ["url"], "output": "markdown" },
    { "name": "browser_use_act", "module": "crawlers", "input": ["instruction"], "output": "html" },
    { "name": "markitdown_convert", "module": "parsers", "input": ["file_path"], "output": "md" },
    { "name": "pdf_master_ocr", "module": "parsers", "input": ["pdf_path"], "output": "text" },
    { "name": "last30days_research", "module": "researchers", "input": ["topic"], "output": "report" },
    { "name": "graphify_build", "module": "researchers", "input": ["repo_path"], "output": "graph" },
    { "name": "headroom_compress", "module": "optimizers", "input": ["text"], "output": "compressed_text" },
    { "name": "skillspector_scan", "module": "security", "input": ["skill_path"], "output": "security_report" }
  ],
  "workflows": {
    "full_pipeline": ["firecrawl_scrape", "markitdown_convert", "headroom_compress", "skillspector_scan"]
  }
}