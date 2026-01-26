#!/bin/bash

# LLM Guard Server 启动脚本
# 支持通过环境变量配置数据源模式

# 默认配置
export DATA_SOURCE_MODE=${DATA_SOURCE_MODE:-"DB"}
export DATA_SOURCE_FILE_BASE_PATH=${DATA_SOURCE_FILE_BASE_PATH:-"data"}

echo "========================================="
echo "LLM Guard Server Starting..."
echo "========================================="
echo "Data Source Mode: $DATA_SOURCE_MODE"

if [ "$DATA_SOURCE_MODE" = "FILE" ]; then
    echo "File Base Path: $DATA_SOURCE_FILE_BASE_PATH"

    # 检查数据目录是否存在
    if [ ! -d "$DATA_SOURCE_FILE_BASE_PATH" ]; then
        echo "ERROR: Data directory not found: $DATA_SOURCE_FILE_BASE_PATH"
        exit 1
    fi

    # 检查必需的JSON文件
    required_files=(
        "global_keywords.json"
        "meta_tags.json"
        "scenario_keywords.json"
        "scenario_policies.json"
        "global_defaults.json"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$DATA_SOURCE_FILE_BASE_PATH/$file" ]; then
            echo "WARNING: Required file not found: $file"
        fi
    done
fi

echo "========================================="

# -u: unbuffered output for real-time logging
python -u start.py
