if __name__ == "__main__":
    # 配置参数
    data_folder = "./raw_data"  # 原始数据文件夹
    output_file = "./cleaned_data/cleaned_data.parquet"  # 清洗后数据保存路径
    
    # 运行自动化流程
    cleaned_data = automated_data_pipeline(data_folder, output_file)
    
    # 可以在这里添加将数据投喂给训练模型的代码
    # train_model(cleaned_data)