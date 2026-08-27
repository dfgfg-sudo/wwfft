# test_system.py - 系统功能验证脚本
import os
import tempfile
import json
import pandas as pd
from pathlib import Path
from main import DataOmnivore, SystemConfig

def test_data_processing():
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    with open(test_dir / "test.txt", "w", encoding="utf-8") as f:
        f.write("测试文本")
    with open(test_dir / "test.json", "w", encoding="utf-8") as f:
        json.dump([{"text": "测试JSON"}], f)
    pd.DataFrame({"text": ["测试CSV"]}).to_csv(test_dir / "test.csv", index=False)
    
    config = SystemConfig()
    loader = DataOmnivore(config)
    data = loader.load_all_data(str(test_dir))
    print(f"加载数据条数: {len(data)}")
    import shutil
    shutil.rmtree(test_dir)
    return len(data) > 0

if __name__ == "__main__":
    if test_data_processing():
        print("✅ 数据加载测试通过")
    else:
        print("❌ 数据加载测试失败")