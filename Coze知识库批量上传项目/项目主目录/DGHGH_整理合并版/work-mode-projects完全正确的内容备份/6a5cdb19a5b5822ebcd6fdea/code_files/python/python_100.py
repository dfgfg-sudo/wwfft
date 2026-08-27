#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bunny系统主入口
"""
import argparse
import logging

from bunny_system.system_core import BunnySystem

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Bunny全栈式智能训练系统")
    parser.add_argument("--data-dir", type=str, help="数据目录路径")
    parser.add_argument("--device", type=str, help="指定设备 (cuda, cuda:0, cpu)")
    parser.add_argument("--host", type=str, help="API服务主机地址")
    parser.add_argument("--port", type=int, help="API服务端口")
    
    args = parser.parse_args()
    
    # 更新配置
    from config import Config
    if args.data_dir:
        Config.data_dir = args.data_dir
    if args.device:
        Config.device = args.device
    if args.host:
        Config.api_host = args.host
    if args.port:
        Config.api_port = args.port
    
    # 创建并运行系统
    system = BunnySystem()
    system.run()

if __name__ == "__main__":
    main()