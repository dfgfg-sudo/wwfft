节点类型: LinkReaderPlugin
输入:
  url: "{{input.url}}"  # 要抓取的网页链接
  type: "全文"          # 可选项：全文/摘要
输出:
  text: 清洗后的正文纯文本
  data.content: 原始HTML解析内容（备用）
  pdf_content: PDF文件提取的文本（仅PDF有效）