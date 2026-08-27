#!/bin/bash
# 启动智能体所有服务

set -e

echo "🔄 启动 Vault 服务..."
docker-compose -f vault/docker-compose.yml up -d

echo "🔄 等待 Vault 就绪..."
sleep 5

echo "🔄 初始化智能体配置..."
python scripts/init_config.py

echo "🔄 启动核心决策引擎..."
nohup python core/decision_engine.py > logs/decision.log 2>&1 &

echo "🔄 启动感知模块..."
nohup python sensors/market_sensor.py > logs/sensor.log 2>&1 &

echo "🔄 启动行动模块..."
nohup python actuators/api_executor.py > logs/executor.log 2>&1 &

echo "🔄 启动审计与熔断..."
nohup python audit/fuse_monitor.py > logs/fuse.log 2>&1 &

echo "✅ 所有服务已启动。查看日志：logs/"