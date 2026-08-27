supported_formats = {
    "文本数据": [".txt", ".md", ".json", ".csv", ".yaml", ".yml"],
    "图像数据": [".jpg", ".png", ".jpeg", ".bmp", ".tiff"],
    "传感器数据": [".csv", ".bag", ".h5", ".mat"],
    "配置数据": [".json", ".yaml", ".ini", ".toml"]
}

processing_pipeline = {
    "步骤1": "格式识别和验证",
    "步骤2": "内容解析和提取",
    "步骤3": "特征计算和转换",
    "步骤4": "数据融合和标准化",
    "步骤5": "缓存管理和索引"
}