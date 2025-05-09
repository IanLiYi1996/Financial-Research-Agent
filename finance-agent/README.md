# 基金投顾多智能体系统 (Fund Advisor Multi-Agent System)

基于multi-agent-orchestrator框架实现的基金投顾多智能体系统，利用AWS云服务存储和检索基金知识图谱和用户信息，通过多个专业agent协同工作，为用户提供全面的基金投资建议。

## 系统架构

![系统架构图](https://raw.githubusercontent.com/awslabs/multi-agent-orchestrator/main/img/flow-supervisor.jpg)

系统包含以下主要组件：

### 1. 主要投顾Agent (Supervisor)

- 作为系统的中央协调者，负责判断用户输入意图，调用相应的专家Agent
- 整合各专家Agent的分析结果，提供综合的投资建议
- 管理用户会话和交互流程

### 2. 用户风险Agent

- 负责从DynamoDB检索和更新用户基本信息
- 评估用户的风险偏好和承受能力
- 将用户的风险评估结果存储到DynamoDB中
- 提供个性化的风险管理建议

### 3. 检索问答Agent

- 从OpenSearch中查询金融知识
- 必要时调用搜索API获取最新金融信息
- 回答用户关于基金和金融投资的知识问题
- 提供专业、准确的金融知识解读

### 4. 基金推荐Agent

- 根据用户信息和查询需求生成查询语句
- 从Nebula知识图谱中检索匹配的基金
- 为用户推荐最适合的基金产品组合
- 解释推荐理由和预期收益风险

## 技术架构

系统利用以下AWS服务和技术：

- **AWS Neptune**：存储基金知识图谱，包含基金之间的关系和属性
- **AWS OpenSearch**：存储基金金融知识，支持全文检索和语义搜索
- **AWS DynamoDB**：存储用户基本信息和风险偏好
- **AWS Bedrock**：提供大语言模型支持，用于智能体的推理和生成
- **Multi-Agent-Orchestrator**：提供多智能体协调框架，管理智能体之间的通信和协作

## 文件结构

```
.
├── main.py                # 主程序文件，包含Agent定义和系统初始化
├── tools.py               # 工具函数文件，实现与AWS服务的交互
├── memory.py              # 记忆系统文件，管理系统的记忆存储和检索
└── README.md              # 项目说明文档
```

## 功能特点

1. **用户风险评估**
   - 根据用户年龄、收入、投资经验等因素评估风险承受能力
   - 将用户风险偏好分为保守型、稳健型、平衡型、成长型、进取型五个等级
   - 存储用户风险偏好和基本信息

2. **金融知识问答**
   - 回答用户关于基金和金融投资的知识问题
   - 提供基金产品知识、金融市场分析、投资策略解读等
   - 获取最新的金融市场信息

3. **基金推荐**
   - 根据用户风险偏好和投资需求推荐合适的基金产品
   - 分析基金的历史表现、风险指标和投资策略
   - 提供个性化的基金组合建议

4. **记忆系统**
   - 存储用户画像和偏好
   - 记录交互历史，实现连续对话
   - 积累金融知识，不断优化推荐质量

## 安装与配置

### 前提条件

- Python 3.8+
- AWS账户及相关服务访问权限
- 配置好的AWS凭证

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/fund-advisor-multi-agent.git
cd fund-advisor-multi-agent
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置AWS凭证：

创建一个`.env`文件，包含以下内容：

```
# AWS凭证
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region

# Bedrock模型设置
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

## 使用方法

运行主程序：

```bash
python main.py
```

系统启动后，用户可以：

1. **更新个人信息和风险偏好**
   ```
   您: 我想更新我的个人信息
   ```

2. **询问金融知识**
   ```
   您: 什么是ETF基金？
   ```

3. **获取基金推荐**
   ```
   您: 请根据我的风险偏好推荐一些基金
   ```

4. **了解特定基金**
   ```
   您: 请告诉我关于华夏成长混合基金的信息
   ```

## 系统流程

1. 用户输入查询或请求
2. 投顾Agent分析用户意图
3. 根据意图调用相应的专家Agent：
   - 风险相关问题 → 用户风险Agent
   - 知识相关问题 → 检索问答Agent
   - 基金推荐请求 → 基金推荐Agent
4. 专家Agent调用相应工具获取所需信息
5. 投顾Agent整合各专家的分析结果
6. 系统向用户提供综合的投资建议

## 示例交互

```
欢迎使用基金投顾多智能体系统。

我是您的投资顾问，我将协调我们的专家团队为您提供投资建议。
我们的专家团队包括：
- 风险分析师：评估您的风险偏好和承受能力
- 知识专家：回答您关于金融和基金投资的问题
- 基金推荐专家：根据您的需求和风险偏好推荐合适的基金产品

您可以：
1. 更新您的个人信息和风险偏好
2. 询问关于基金和金融投资的知识
3. 获取基于您风险偏好的基金推荐
4. 了解特定基金的详细信息

您: 我是一名35岁的工程师，年收入30万，有5年投资经验，想为孩子教育和退休做规划，我适合什么风险等级？

风险分析师: 根据您提供的信息，您35岁，作为工程师年收入30万，有5年投资经验，投资目标是子女教育和退休规划。考虑到您的年龄、收入水平和投资经验，以及长期投资目标，我建议您采用平衡型的风险等级。平衡型投资组合追求收益和风险的平衡，适合您这样风险承受能力中等的投资者。我已将您的信息更新到系统中。

您: 请推荐一些适合我的基金

基金推荐专家: 根据您的平衡型风险偏好和子女教育与退休规划的投资目标，我为您推荐以下基金组合：

1. 华夏成长混合基金 (000001)
   - 风险等级：平衡型
   - 年化收益(近1年)：8.23%
   - 投资策略：投资于具有良好成长性的上市公司股票
   - 推荐理由：风险等级与您的偏好匹配，长期业绩稳定

2. 嘉实沪深300ETF (000003)
   - 风险等级：成长型
   - 年化收益(近1年)：9.12%
   - 投资策略：跟踪沪深300指数
   - 推荐理由：提供市场平均表现，费用低廉

3. 南方货币A (000005)
   - 风险等级：保守型
   - 年化收益(近1年)：2.34%
   - 投资策略：投资于货币市场工具
   - 推荐理由：作为投资组合的稳定部分，提供流动性

建议配置比例：50% 华夏成长混合、30% 嘉实沪深300ETF、20% 南方货币A，这样可以在追求长期增长的同时控制整体风险。

您: 什么是ETF基金？

知识专家: ETF(Exchange Traded Fund)是交易型开放式指数基金，它结合了开放式基金和封闭式基金的优点。ETF在证券交易所上市交易，投资者可以像买卖股票一样买卖ETF份额。

ETF的主要特点包括：
1. 透明度高：ETF的持仓通常每日公布
2. 交易便捷：可以在交易时间内随时买卖
3. 费用低廉：管理费和交易成本通常低于主动管理型基金
4. 追踪指数：大多数ETF追踪特定指数，如沪深300指数、标普500指数等

ETF适合希望获得与特定市场或行业表现一致回报的投资者，也是资产配置和分散投资的有效工具。您推荐组合中的嘉实沪深300ETF就是一种典型的ETF，它追踪沪深300指数，反映中国A股市场整体表现。
```

## 扩展与定制

该系统设计具有良好的扩展性：

1. **添加新的专家Agent**：可以根据需要添加新的专家Agent，如税务规划Agent、海外投资Agent等
2. **集成更多数据源**：可以集成更多的外部数据源，如市场新闻、宏观经济数据等
3. **扩展记忆系统**：可以扩展记忆系统以存储更多类型的信息，如市场预测、投资日志等
4. **自定义推荐算法**：可以根据特定需求定制基金推荐算法

## 注意事项

- 该系统提供的投资建议仅供参考，不构成投资决策依据
- 实际部署时需确保AWS服务配置正确，并有适当的权限管理
- 用户数据应遵循相关法规进行保护和处理

## 许可证

[MIT License](LICENSE)

## 贡献指南

欢迎贡献代码或提出建议，请遵循以下步骤：

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 联系方式

如有问题或建议，请联系：your-email@example.com
