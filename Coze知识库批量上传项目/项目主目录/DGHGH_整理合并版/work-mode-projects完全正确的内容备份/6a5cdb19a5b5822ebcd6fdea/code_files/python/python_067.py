#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API服务模块
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime
import os
from pathlib import Path
import logging

logger = logging.getLogger("BunnySystem")

# 全局状态
training_active = False
current_trainer = None

app = FastAPI(
    title="Bunny全栈式智能训练系统",
    description="多模态智能训练平台 v13.0",
    version="13.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class TrainingRequest(BaseModel):
    """训练请求模型"""
    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 1e-4
    model_type: str = "distillation"

class SystemStatus(BaseModel):
    """系统状态模型"""
    status: str
    timestamp: str
    active_training: bool = False

class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    status: str
    filename: str
    saved_path: str
    message: str

@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "Bunny全栈式智能训练系统 v13.0",
        "status": "运行中",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def get_status():
    """获取系统状态"""
    from .device_manager import DeviceManager
    
    device_mgr = DeviceManager()
    
    return SystemStatus(
        status="running",
        timestamp=datetime.now().isoformat(),
        active_training=training_active
    )

@app.post("/start_training")
async def start_training(request: TrainingRequest):
    """启动训练"""
    global training_active, current_trainer
    
    if training_active:
        return {"status": "error", "message": "训练正在进行中"}
    
    try:
        training_active = True
        
        # 异步执行训练
        asyncio.create_task(run_training_async(request))
        
        return {
            "status": "success", 
            "message": "训练已开始",
            "config": request.dict()
        }
        
    except Exception as e:
        training_active = False
        logger.error(f"启动训练失败: {str(e)}")
        return {"status": "error", "message": f"训练启动失败: {str(e)}"}

async def run_training_async(request):
    """异步运行训练"""
    global training_active
    try:
        # 这里应该实现实际的训练逻辑
        logger.info(f"开始训练，配置: {request.dict()}")
        await asyncio.sleep(1)  # 模拟训练过程
        logger.info("训练完成")
    except Exception as e:
        logger.error(f"训练过程出错: {str(e)}")
    finally:
        training_active = False

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """文件上传接口"""
    try:
        from config import Config
        
        # 确保数据目录存在
        os.makedirs(Config.data_dir, exist_ok=True)
        
        # 保存文件
        file_location = os.path.join(Config.data_dir, file.filename)
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"文件上传成功: {file.filename}")
        
        return FileUploadResponse(
            status="success",
            filename=file.filename,
            saved_path=file_location,
            message="文件上传成功"
        )
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return {"status": "error", "message": f"文件上传失败: {str(e)}"}

@app.get("/files")
async def list_files():
    """列出所有文件"""
    try:
        from config import Config
        
        files = []
        for file_path in Path(Config.data_dir).rglob("*"):
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "type": file_path.suffix
                })
        
        return {"status": "success", "files": files}
    except Exception as e:
        return {"status": "error", "message": str(e)}