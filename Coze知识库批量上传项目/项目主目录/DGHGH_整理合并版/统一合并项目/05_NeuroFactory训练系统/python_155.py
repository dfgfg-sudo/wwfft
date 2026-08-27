# 在SmartFileHandler中添加自定义处理逻辑
def process_csv(self, file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df = df.drop_duplicates()  # 自动去重
    return df