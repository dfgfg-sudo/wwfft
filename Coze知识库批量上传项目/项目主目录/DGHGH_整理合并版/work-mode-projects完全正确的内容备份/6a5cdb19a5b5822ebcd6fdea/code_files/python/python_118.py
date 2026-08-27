#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bunny全栈式智能训练系统安装配置
"""
from setuptools import setup, find_packages

setup(
    name="bunny-system",
    version="13.0.0",
    description="Bunny全栈式智能训练系统",
    author="Bunny AI Team",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "watchdog>=3.0.0",
        "PyMuPDF>=1.23.0",
        "pandas>=2.0.0",
        "Pillow>=10.0.0",
        "pydantic>=2.0.0"
    ],
    python_requires=">=3.8",
)