# HedgeAgents

HedgeAgents是一个基于multi-agent-orchestrator框架的对冲基金多智能体系统。该系统模拟了一个由对冲基金经理和多个专业分析师组成的团队，用于市场分析和投资决策。

## 系统架构

![HedgeAgents架构](https://raw.githubusercontent.com/awslabs/multi-agent-orchestrator/main/img/flow-supervisor.jpg)

HedgeAgents系统包括以下组件：

1. **专业分析师智能体**：
   - 比特币分析师Dave：专注于加密货币市场分析
   - DJ30分析师Bob：专注于股票市场分析
   - 外汇分析师Emily：专注于外汇市场分析

2. **对冲基金经理Otto**：
   - 作为SupervisorAgent，协调分析师团队
   - 整合分析结果，做出最终投资决策

3. **工具系统**：
   - 技术指标分析工具：分析RSI、MACD、移动平均线等技术指标
   - 市场动态注释工具：分析市场波动性、趋势、成交量等
   - 新闻分析工具：分析与资产相关的新闻，评估市场情绪

4. **记忆系统**：
   - 市场信息记忆：存储市场数据和分析结果
   - 投资反思记忆：存储过去投资决策的经验教训
   - 一般经验记忆：存储通用的投资原则和知识

5. **会议系统**：
   - 预算分配会议：决定如何分配投资预算到不同资产类别
   - 经验分享会议：分享和讨论投资经验，提高团队决策能力
   - 极端市场会议：应对极端市场情况，制定危机应对策略

## 安装

1. 安装依赖项：

```bash
pip install -r requirements.txt
```

2. 设置环境变量：

创建一个`.env`文件，包含以下内容：

```
# AWS凭证（如果使用AWS Bedrock）
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region

# 可选：Anthropic API密钥（如果使用Anthropic Claude）
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## 使用方法

运行主程序：

```bash
python -m hedge_agents.main
```

系统启动后，您可以：

1. 询问特定市场的分析和建议
2. 请求召开预算分配会议
3. 请求召开经验分享会议
4. 请求召开极端市场会议
5. 获取综合投资建议

示例输入：

- "比特币市场现在如何？"
- "请分析道琼斯指数的技术指标"
- "欧元兑美元的走势如何？"
- "请召开预算分配会议"
- "我们需要讨论极端市场情况"

## 自定义

您可以通过修改以下文件来自定义系统：

- `tools.py`：添加或修改市场分析工具
- `memory.py`：调整记忆系统的行为
- `conferences.py`：修改会议提示和模板
- `main.py`：调整智能体配置和系统行为

## 依赖项

- multi-agent-orchestrator：多智能体协调框架
- boto3：AWS SDK for Python（用于访问AWS Bedrock）
- python-dotenv：环境变量管理

## 注意事项

- 该系统需要访问AWS Bedrock或Anthropic API来使用LLM模型
- 系统中的市场数据为模拟数据，仅用于演示目的
- 该系统不应用于实际投资决策，仅供研究和教育目的使用
