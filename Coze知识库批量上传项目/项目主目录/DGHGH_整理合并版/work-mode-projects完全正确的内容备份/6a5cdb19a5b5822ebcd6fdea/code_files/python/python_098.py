def clean_data(raw_df):
    """
    数据清洗处理函数
    
    参数:
        raw_df: 原始数据DataFrame
    
    返回:
        清洗后的DataFrame
    """
    # 1. 去除完全重复的行
    cleaned_df = raw_df.drop_duplicates()
    
    # 2. 处理缺失值
    # 数值列用中位数填充
    num_cols = cleaned_df.select_dtypes(include=['number']).columns
    for col in num_cols:
        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
    
    # 分类列用众数填充
    cat_cols = cleaned_df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0])
    
    # 3. 处理异常值 - 使用IQR方法
    for col in num_cols:
        Q1 = cleaned_df[col].quantile(0.25)
        Q3 = cleaned_df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 将异常值替换为边界值
        cleaned_df[col] = cleaned_df[col].clip(lower_bound, upper_bound)
    
    # 4. 标准化文本数据 (去除前后空格，统一大小写等)
    for col in cat_cols:
        cleaned_df[col] = cleaned_df[col].str.strip().str.lower()
    
    return cleaned_df