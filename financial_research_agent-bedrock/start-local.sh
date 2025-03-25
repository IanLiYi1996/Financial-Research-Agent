#!/bin/bash
# start-local.sh - 在本地启动Financial Research Agent

echo "===== 启动本地Financial Research Agent ====="

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请安装Node.js后再试"
    exit 1
fi

# 检查Python是否安装
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请安装Python后再试"
    exit 1
fi

# 检查AWS CLI是否配置
if [ ! -f ~/.aws/credentials ]; then
    echo "警告: 未找到AWS凭证，请确保已配置AWS CLI"
    echo "是否继续? (y/n)"
    read answer
    if [ "$answer" != "y" ]; then
        exit 1
    fi
fi

# 安装依赖
echo "正在安装依赖..."
pip install -r requirements.txt

# 安装Node.js依赖
echo "正在安装Node.js依赖..."
npm install express cors body-parser

# 准备Lambda层
echo "正在准备Lambda层..."
mkdir -p lambdas/layer/python
pip install -r lambdas/layer/requirements.txt -t lambdas/layer/python/

# 检查配置文件
if [ ! -f config.local.json ]; then
    echo "错误: 未找到config.local.json配置文件"
    exit 1
fi

# 检查API密钥
API_KEY=$(grep -o '"apiKey": "[^"]*"' config.local.json | cut -d'"' -f4)
if [ "$API_KEY" == "YOUR_SEARCH_API_KEY" ]; then
    echo "警告: 搜索API密钥未配置，搜索功能可能无法正常工作"
fi

# 启动本地服务器
echo "正在启动本地服务器..."
node local-server.js &
SERVER_PID=$!

echo "===== 本地服务已启动 ====="
echo "API服务器: http://localhost:3000"
echo "前端界面: http://localhost:3000"
echo "按Ctrl+C停止服务"

# 捕获终止信号，关闭服务器
trap "kill $SERVER_PID; echo '服务已停止'" INT TERM
wait
