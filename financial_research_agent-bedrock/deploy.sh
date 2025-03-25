#!/bin/bash
# deploy.sh - 一键部署Financial Research Agent

echo "===== 开始部署Financial Research Agent ====="

# 1. 安装依赖
echo "正在安装依赖..."
pip install -r requirements.txt

# 2. 设置AWS凭证（如果尚未配置）
if [ ! -f ~/.aws/credentials ]; then
    echo "请输入AWS凭证信息："
    aws configure
fi

# 3. 准备Lambda层
echo "正在准备Lambda层..."
mkdir -p lambdas/layer/python
pip install -r lambdas/layer/requirements.txt -t lambdas/layer/python/

# 4. 部署CDK堆栈
echo "正在部署CDK堆栈..."
cd cdk
npm install -g aws-cdk
pip install -r requirements.txt
cdk bootstrap
cdk deploy --require-approval never
cd ..

# 5. 获取API Gateway URL并更新前端配置
echo "正在更新前端配置..."
API_URL=$(aws cloudformation describe-stacks --stack-name FinancialResearchStack --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)
sed -i "s|https://your-api-gateway-url.amazonaws.com/prod/research|$API_URL|g" frontend/script.js

# 6. 启动本地前端服务器
echo "正在启动本地前端服务器..."
cd frontend
python -m http.server 8080 &
FRONTEND_PID=$!

echo "===== 部署完成 ====="
echo "前端服务已启动在: http://localhost:8080"
echo "按Ctrl+C停止服务"

# 捕获终止信号，关闭前端服务器
trap "kill $FRONTEND_PID; echo '服务已停止'" INT TERM
wait
