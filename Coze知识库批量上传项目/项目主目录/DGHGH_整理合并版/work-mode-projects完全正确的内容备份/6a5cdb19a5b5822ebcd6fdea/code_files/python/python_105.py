def automated_data_pipeline(data_folder, output_file=None):
    """
    完整的数据自动化处理流程
    
    参数:
        data_folder: 原始数据文件夹路径
        output_file: 清洗后数据保存路径(可选)
    
    返回:
        清洗后的DataFrame
    """
    # 1. 自动收集数据
    print("正在收集原始数据...")
    raw_data = load_data_from_folder(data_folder)
    print(f"收集到 {len(raw_data)} 条原始记录")
    
    # 2. 数据清洗
    print("正在进行数据清洗...")
    cleaned_data = clean_data(raw_data)
    print(f"清洗后保留 {len(cleaned_data)} 条有效记录")
    
    # 3. 可选: 保存清洗后的数据
    if output_file:
        if output_file.endswith('.csv'):
            cleaned_data.to_csv(output_file, index=False)
        elif output_file.endswith('.parquet'):
            cleaned_data.to_parquet(output_file, index=False)
        print(f"清洗后的数据已保存到 {output_file}")
    
    return cleaned_data