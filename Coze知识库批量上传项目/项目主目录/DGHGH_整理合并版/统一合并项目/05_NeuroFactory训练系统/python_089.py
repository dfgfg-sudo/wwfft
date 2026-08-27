#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件监控模块
"""
import time
import threading
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import logging

logger = logging.getLogger("BunnySystem")

class FileMonitor(FileSystemEventHandler):
    """实时文件监控处理器"""
    
    def __init__(self, processor, callback=None):
        super().__init__()
        self.processor = processor
        self.callback = callback
        self.processed_files = set()
    
    def on_created(self, event):
        """文件创建事件处理"""
        if not event.is_directory:
            logger.info(f"检测到新文件: {event.src_path}")
            self._process_with_delay(event.src_path)
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if not event.is_directory:
            logger.info(f"文件被修改: {event.src_path}")
            self._process_with_delay(event.src_path)
    
    def _process_with_delay(self, filepath, delay=1):
        """延迟处理文件"""
        def process():
            time.sleep(delay)
            self.process_file(filepath)
        
        threading.Thread(target=process, daemon=True).start()
    
    def process_file(self, path):
        """处理文件"""
        filepath = Path(path)
        file_id = f"{filepath}_{filepath.stat().st_mtime}"
        
        if file_id in self.processed_files:
            return
        
        try:
            result = self.processor.process_file(path)
            if result is not None:
                self.processed_files.add(file_id)
                logger.info(f"成功处理文件: {path}")
                
                if self.callback:
                    self.callback(path, result)
        except Exception as e:
            logger.error(f"处理文件 {path} 时出错: {str(e)}")