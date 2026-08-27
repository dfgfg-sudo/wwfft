#!/usr/bin/env bash
# -*- coding: utf-8 -*-
set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"; }

check_dependencies() {
    command -v python3 &>/dev/null || { log_error "Python3 未安装"; exit 1; }
    command -v pip3 &>/dev/null || { log_error "pip3 未安装"; exit 1; }
}

install_requirements() {
    log_info "安装依赖..."
    pip3 install -r requirements.txt || { log_error "依赖安装失败"; exit 1; }
}

prepare_data() {
    mkdir -p ./data
    [ -f ./data/train.txt ] || echo "示例训练数据" > ./data/train.txt
}

run_training() {
    log_info "启动训练..."
    python3 neurofactory_fusion.py
    log_info "训练完成"
}

main() {
    check_dependencies
    install_requirements
    prepare_data
    run_training
}
main "$@"