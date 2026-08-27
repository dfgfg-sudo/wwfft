# auto_trainer.py
import os
import json
import logging
import torch
import zipfile
import csv
import hashlib
import threading
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from collections import deque
from concurrent.futures import TAI训练工厂 v3.0 - 终极完整版文档

📖 项目概述

项目名称：AI训练工厂 v3.0 (AI Training Factory v3.0)

项目目标：提供一套全自动、多数据源、可视化的人工智能模型训练系统，支持文本、图像、表格、PDF、Word、Excel等多种数据格式，并通过LoRA高效微调技术，在CPU/GPU环境下快速训练自定义语言模型。

核心特性：

· ✅ 全自动数据处理（自动识别格式、解压ZIP、清洗去重）
· ✅ 一键式模型训练（加载预训练模型 → LoRA微调 → 输出成品）
· ✅ 可视化图形界面（进度监控、日志记录、状态提示）
· ✅ 多线程加速（数据加载与训练并行）
· ✅ 增量学习能力（可反复追加新数据继续训练）
· ✅ 极简项目结构（仅需三个核心目录 + 两个启动文件）

---

🏗️ 系统架构图（Mermaid）