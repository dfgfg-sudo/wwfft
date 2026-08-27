#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bunny全栈式智能训练系统主包
"""

from .device_manager import DeviceManager
from .multimodal_processor import MultiModalProcessor
from .dataset import MultiModalDataset
from .file_monitor import FileMonitor
from .models import SelfHealingModel, TeacherModel, StudentModel
from .trainer import DistillationTrainer
from .distributed import setup_distributed, cleanup_distributed
from .api_server import app, training_active, current_trainer
from .system_core import BunnySystem

__version__ = "13.0.0"
__all__ = [
    "DeviceManager",
    "MultiModalProcessor",
    "MultiModalDataset",
    "FileMonitor",
    "SelfHealingModel",
    "TeacherModel",
    "StudentModel",
    "DistillationTrainer",
    "setup_distributed",
    "cleanup_distributed",
    "app",
    "training_active",
    "current_trainer",
    "BunnySystem"
]