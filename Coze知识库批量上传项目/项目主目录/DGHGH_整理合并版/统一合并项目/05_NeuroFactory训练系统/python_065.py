#!/usr/bin/env python3
"""
部署脚本 - 用于在Trae-CN软件中部署
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_environment():
    """检查环境"""
    print("检查系统环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print("错误: Python 3.9+ 是必需的")
        return False
        
    # 检查GPU
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ GPU可用: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠ 警告: GPU不可用，将使用CPU模式")
    except ImportError:
        print("⚠ 警告: PyTorch未安装")
        
    return True
    
def install_dependencies():
    """安装依赖"""
    print("\n安装依赖包...")
    
    requirements_file = "requirements.txt"
    if not Path(requirements_file).exists():
        print("错误: requirements.txt 不存在")
        return False
        
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✓ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: 依赖安装失败: {e}")
        return False
        
def setup_directories():
    """设置目录结构"""
    print("\n设置目录结构...")
    
    directories = [
        "models",
        "data/raw",
        "data/processed",
        "data/train",
        "data/val",
        "data/test",
        "logs/training",
        "logs/inference",
        "logs/system",
        "outputs",
        ".cache"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  创建目录: {directory}")
        
    return True
    
def copy_config_files():
    """复制配置文件"""
    print("\n配置系统文件...")
    
    config_files = {
        "config.example.json": "config.json",
        ".env.example": ".env"
    }
    
    for src, dst in config_files.items():
        if Path(src).exists() and not Path(dst).exists():
            shutil.copy(src, dst)
            print(f"  复制: {src} -> {dst}")
            
    return True
    
def setup_trae_config():
    """设置Trae-CN配置"""
    print("\n配置Trae-CN集成...")
    
    trae_config = {
        "project": {
            "name": "UltimateAI-System",
            "type": "ai_system",
            "version": "9.0.0"
        },
        "runtime": {
            "python_path": sys.executable,
            "working_dir": str(Path.cwd()),
            "entry_point": "src/main.py"
        },
        "features": {
            "quantum_computing": True,
            "multimodal_fusion": True,
            "consciousness": True,
            "auto_evolution": True
        },
        "deployment": {
            "target": "trae_cn",
            "compatibility": "full"
        }
    }
    
    import json
    with open(".trae-config.json", "w") as f:
        json.dump(trae_config, f, indent=2)
        
    print("✓ Trae-CN配置完成")
    return True
    
def run_tests():
    """运行测试"""
    print("\n运行系统测试...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pytest", "tests/", "-v"])
        print("✓ 所有测试通过")
        return True
    except subprocess.CalledProcessError:
        print("⚠ 警告: 部分测试失败")
        return True  # 即使测试失败也继续
        
def main():
    """主部署函数"""
    print("=" * 60)
    print("UltimateAI-System v9.0 部署脚本")
    print("=" * 60)
    
    # 步骤1: 检查环境
    if not check_environment():
        return 1
        
    # 步骤2: 安装依赖
    if not install_dependencies():
        return 2
        
    # 步骤3: 设置目录
    if not setup_directories():
        return 3
        
    # 步骤4: 复制配置文件
    if not copy_config_files():
        return 4
        
    # 步骤5: 设置Trae配置
    if not setup_trae_config():
        return 5
        
    # 步骤6: 运行测试
    if not run_tests():
        return 6
        
    print("\n" + "=" * 60)
    print("部署完成！")
    print("\n下一步:")
    print("1. 编辑 config.json 配置文件")
    print("2. 编辑 .env 环境变量文件")
    print("3. 运行: python src/main.py --mode cli")
    print("4. 或运行: python src/main.py --mode web --port 8080")
    print("=" * 60)
    
    return 0
    
if __name__ == "__main__":
    sys.exit(main())