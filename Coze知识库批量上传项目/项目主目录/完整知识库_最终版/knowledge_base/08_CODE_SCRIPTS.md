# 📦 脚本代码库

## 📋 概述

收集了Python、PowerShell等多种脚本语言的实用工具脚本，用于自动化任务处理和数据管理。

---

## 🐍 Python脚本

### 1. 数据处理脚本

```python
#!/usr/bin/env python3
"""数据处理工具集"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

def load_csv_file(file_path):
    """加载CSV文件"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        return df
    except Exception as e:
        print(f"加载CSV文件失败: {e}")
        return None

def save_to_csv(df, file_path):
    """保存DataFrame到CSV"""
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"文件已保存: {file_path}")
        return True
        print(f"保存CSV文件失败: {e}")
        return False

def load_json_file(file_path):
    """加载JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
        print(f"加载JSON文件失败: {e}")

def save_to_json(data, file_path, indent=2):
    """保存数据到JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        print(f"保存JSON文件失败: {e}")

def clean_dataframe(df):
    """清理DataFrame数据"""
    # 去除重复行
    df = df.drop_duplicates()
    
    # 填充缺失值
    df = df.fillna('')
    
    # 重置索引
    df = df.reset_index(drop=True)
    

def merge_multiple_csv(files, output_path):
    """合并多个CSV文件"""
    dfs = []
    for file in files:
        if os.path.exists(file):
            df = load_csv_file(file)
            if df is not None:
                dfs.append(df)
    
    if dfs:
        merged_df = pd.concat(dfs, ignore_index=True)
        merged_df = clean_dataframe(merged_df)
        save_to_csv(merged_df, output_path)
        return merged_df
```

### 2. 文件管理脚本

```python
#!/usr/bin/env python3
"""文件管理工具"""

import shutil
from pathlib import Path

def list_files(directory, extension=None):
    """列出目录中的文件"""
    files = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            if extension is None or item.endswith(extension):
                files.append(item_path)
    return sorted(files)

def create_directory(path):
    """创建目录"""
        os.makedirs(path, exist_ok=True)
        print(f"创建目录失败: {e}")

def copy_files(source_files, destination_dir):
    """复制文件到目标目录"""
    create_directory(destination_dir)
    copied_count = 0
    
    for source in source_files:
        if os.path.isfile(source):
            filename = os.path.basename(source)
            destination = os.path.join(destination_dir, filename)
            shutil.copy2(source, destination)
            copied_count += 1
    
    print(f"已复制 {copied_count} 个文件")
    return copied_count

def backup_files(source_dir, backup_dir):
    """备份目录中的文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
    create_directory(backup_path)
    
    files = list_files(source_dir)
    copy_files(files, backup_path)
    
    return backup_path
```

### 3. 日志记录脚本

```python
#!/usr/bin/env python3
"""日志记录工具"""

import logging

def setup_logger(name, log_dir='logs', level=logging.INFO):
    """设置日志记录器"""
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 文件处理器
    log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    

def log_execution_time(func):
    """记录函数执行时间的装饰器"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger = logging.getLogger(func.__name__)
        
            result = func(*args, **kwargs)
            elapsed_time = datetime.now() - start_time
            logger.info(f"函数 {func.__name__} 执行完成，耗时 {elapsed_time}")
            return result
            logger.error(f"函数 {func.__name__} 执行失败: {e}")
            raise
    
    return wrapper
```


## 📜 PowerShell脚本

### 1. 文件操作脚本

```powershell
<#
.SYNOPSIS
    文件操作工具集
#>

function Get-FileList {
        获取目录中的文件列表
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path,
        
        [string]$Extension = $null
    
    if (-not (Test-Path $Path)) {
        Write-Error "路径不存在: $Path"
        return
    }
    
    $files = Get-ChildItem -Path $Path -File
    
    if ($Extension) {
        $files = $files | Where-Object { $_.Extension -eq $Extension }
    
    return $files

function Copy-FilesToDirectory {
        复制文件到目标目录
    #>
        [string[]]$SourceFiles,
        
        [string]$Destination
    
    if (-not (Test-Path $Destination)) {
        New-Item -ItemType Directory -Path $Destination | Out-Null
    
    $copiedCount = 0
    foreach ($file in $SourceFiles) {
        if (Test-Path $file -PathType Leaf) {
            $fileName = Split-Path $file -Leaf
            $destPath = Join-Path $Destination $fileName
            Copy-Item -Path $file -Destination $destPath -Force
            $copiedCount++
    
    Write-Host "已复制 $copiedCount 个文件"
    return $copiedCount

function Backup-Directory {
        备份目录内容
    #>
        [string]$Source,
        
        [string]$BackupRoot = "backups"
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = Join-Path $BackupRoot "backup_$timestamp"
    
    if (-not (Test-Path $BackupRoot)) {
        New-Item -ItemType Directory -Path $BackupRoot | Out-Null
    
    Copy-Item -Path $Source -Destination $backupPath -Recurse -Force
    Write-Host "备份已创建: $backupPath"
    
    return $backupPath
```

### 2. 数据处理脚本

```powershell
    数据处理工具集
#>

function ConvertTo-JsonPretty {
        将对象转换为格式化的JSON字符串
    #>
        [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
        [object]$InputObject,
        
        [int]$Indent = 2
    
    $json = $InputObject | ConvertTo-Json -Depth 100
    return $json

function Merge-CsvFiles {
        合并多个CSV文件
    #>
        [string[]]$Files,
        
        [string]$OutputPath
    
    $dataFrames = @()
    foreach ($file in $Files) {
        if (Test-Path $file) {
            $df = Import-Csv -Path $file -Encoding UTF8
            $dataFrames += $df
    
    if ($dataFrames.Count -gt 0) {
        $merged = $dataFrames | Select-Object -Unique
        $merged | Export-Csv -Path $OutputPath -Encoding UTF8 -NoTypeInformation
        Write-Host "合并完成，已保存到: $OutputPath"
        return $merged
    
    return $null
```


## 📁 脚本目录结构

```
scripts/
├── python/
│   ├── data_processor.py     # 数据处理工具
│   ├── file_manager.py       # 文件管理工具
│   ├── logger.py             # 日志记录工具
│   └── utils.py              # 通用工具函数
├── powershell/
│   ├── FileOps.ps1           # 文件操作脚本
│   ├── DataProcessing.ps1    # 数据处理脚本
│   └── BackupTools.ps1       # 备份工具脚本
└── README.md                 # 脚本说明文档
```


## 📎 相关文档

- [数据处理模块](09_DATA_PROCESSING.md) - 数据处理工具
- [系统架构设计](10_SYSTEM_ARCHITECTURE.md) - 完整技术栈描述