# 自定义数据处理器示例
def handle_custom_format(file_path: str) -> Any:
    """处理自定义格式文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        # 实现自定义处理逻辑
        return processed_data

# 注册到系统
asi.ingestion.handler.file_processors['.myformat'] = handle_custom_format