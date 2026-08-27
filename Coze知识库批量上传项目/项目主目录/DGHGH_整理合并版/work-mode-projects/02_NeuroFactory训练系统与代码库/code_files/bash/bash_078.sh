# 安装测试依赖
pip install pytest pytest-cov

# 运行测试
pytest tests/

# 运行测试并生成覆盖率报告
pytest --cov=src tests/