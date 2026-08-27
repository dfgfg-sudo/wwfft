from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="amm-ats",
    version="1.0.0",
    author="AMM-ATS Team",
    description="全自动多模态AI训练系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.9.0",
        "torchvision>=0.10.0",
        "transformers>=4.12.0",
        "timm>=0.5.4",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "pillow>=8.3.0",
        "scikit-learn>=0.24.0",
        "tensorboard>=2.7.0",
        "tqdm>=4.62.0",
    ],
    entry_points={
        "console_scripts": [
            "amm-ats=main:main",
        ],
    },
)