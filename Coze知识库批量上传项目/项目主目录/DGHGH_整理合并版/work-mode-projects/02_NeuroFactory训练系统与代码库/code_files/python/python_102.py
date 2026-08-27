import os
import pandas as pd
from glob import glob

def load_data_from_folder(folder_path, file_pattern="*.csv"):
    """
    自动化获取文件夹中的本地存储数据
    
    参数:
        folder_path: 数据文件夹路径
        file_pattern: 文件匹配模式(如"*.csv", "*.xlsx")
    
    返回:
        合并后的DataFrame
    """
    # 获取所有匹配的文件
    file_paths = glob(os.path.join(folder_path, file_pattern))
    
    # 读取并合并所有文件
    dfs = []
    for file_path in file_paths:
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            else:
                continue
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
    
    if not dfs:
        raise ValueError("No valid data files found in the specified folder")
    
    return pd.concat(dfs, ignore_index=True)