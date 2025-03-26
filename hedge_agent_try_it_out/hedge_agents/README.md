# HedgeAgents

HedgeAgents是一个基于multi-agent-orchestrator框架的对冲基金多智能体系统。该系统模拟了一个由对冲基金经理和多个专业分析师组成的团队，用于市场分析和投资决策。

## 业务需求

在当今复杂多变的金融市场环境中，投资机构面临以下关键挑战：

- **数据处理与分析压力**：金融市场每日产生海量数据，传统分析方法难以高效处理
- **多市场信息整合难度**：股票、外汇、加密货币等多个市场的信息需要同时监控和分析
- **决策速度与质量平衡**：市场瞬息万变，需要在短时间内做出高质量的投资决策
- **专业知识协同问题**：不同领域的专家知识需要有效整合，形成综合判断
- **风险管理复杂性**：需要全面评估多维度风险因素，制定有效的风险控制策略
- **投资策略一致性**：确保投资决策符合机构整体战略目标和风险偏好

## 解决方案

作为AWS builder，我们提供基于AWS云服务的HedgeAgents多智能体系统解决方案：

- **基础模型服务**：利用AWS Bedrock提供高性能、可扩展的基础语言模型能力，支持各专业智能体的分析推理
- **无服务器架构**：通过AWS Lambda实现各智能体的无服务器部署，确保系统弹性扩展和高可用性
- **数据存储与管理**：
  - 使用Amazon S3存储市场历史数据和分析结果
  - 利用Amazon DynamoDB实现智能体记忆系统，支持快速读写和实时决策
- **系统监控与管理**：
  - 通过Amazon CloudWatch监控系统性能和智能体行为
  - 使用AWS Step Functions编排复杂的多智能体工作流
- **安全与合规**：
  - 利用AWS IAM实现精细的访问控制
  - 通过AWS KMS加密敏感数据，确保投资策略安全
- **部署与集成**：
  - 使用AWS CDK实现基础设施即代码，简化部署流程
  - 通过Amazon API Gateway提供RESTful API，便于与现有系统集成

## 收益

实施HedgeAgents解决方案为金融机构带来以下显著价值：

- **提升决策质量**：通过多专家智能体协作，全面分析市场信息，提高投资决策准确性
- **加速分析流程**：将传统需要数小时的市场分析缩短至分钟级，提高市场响应速度
- **降低运营成本**：自动化分析流程，减少50%以上的人工分析时间，优化资源配置
- **增强风险管理**：全面评估多维度风险因素，提前识别潜在风险，降低投资损失概率
- **知识积累与传承**：智能体记忆系统持续积累投资经验，形成机构知识资产
- **可扩展性**：轻松扩展新的市场分析领域和投资策略，适应不断变化的市场环境
- **合规与审计**：自动记录决策过程，提供完整审计跟踪，满足监管要求

## 系统架构

![HedgeAgents架构](https://raw.githubusercontent.com/awslabs/multi-agent-orchestrator/main/img/flow-supervisor.jpg)

## 智能体调用流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant HFM as 对冲基金经理(Otto)
    participant DJ30 as DJ30分析师(Bob)
    participant FX as 外汇分析师(Emily)
    participant BTC as 比特币分析师(Dave)
    
    User->>HFM: 发送市场分析请求
    
    alt 股票市场相关
        HFM->>DJ30: 请求股票市场分析
        DJ30-->>HFM: 返回股票市场分析结果
    end
    
    alt 外汇市场相关
        HFM->>FX: 请求外汇市场分析
        FX-->>HFM: 返回外汇市场分析结果
    end
    
    alt 加密货币市场相关
        HFM->>BTC: 请求加密货币市场分析
        BTC-->>HFM: 返回加密货币市场分析结果
    end
    
    HFM->>User: 整合分析结果，提供综合建议
```

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
cd hedge_agents
python -m main
```

系统启动后，您可以：

1. 询问特定市场的分析和建议
2. 请求召开预算分配会议
3. 请求召开经验分享会议
4. 请求召开极端市场会议
5. 获取综合投资建议

### 示例输入：

- "比特币市场现在如何？"
- "请分析道琼斯指数的技术指标"
- "欧元兑美元的走势如何？"
- "请召开预算分配会议"
- "我们需要讨论极端市场情况"

### 交互示例：

以下是一个具体的交互示例，展示了用户询问"标普500最近怎么样"时的系统处理流程：

```mermaid
sequenceDiagram
    participant User as 用户
    participant HFM as 对冲基金经理(Otto)
    participant DJ30 as DJ30分析师(Bob)
    participant FX as 外汇分析师(Emily)
    
    User->>HFM: 标普500最近怎么样?
    
    HFM->>DJ30: 请总结一下最近标普500指数的表现
    HFM->>FX: 请评估一下标普500指数最近的走势对美元的影响
    
    Note over DJ30: 分析标普500指数表现
    DJ30-->>HFM: 标普500指数有所上涨，受益于良好的企业财报和经济数据<br/>但通胀压力和加息预期带来不确定性<br/>建议保持谨慎乐观，控制风险敞口
    
    Note over FX: 分析标普500与美元关系
    FX-->>HFM: 标普500与美元指数存在负相关关系<br/>美国经济数据向好有利于美元走强<br/>但地缘政治风险和通胀压力可能限制美元涨幅
    
    Note over HFM: 整合分析结果
    HFM->>User: 标普500指数最近表现稳健，反映投资者信心<br/>与美元存在负相关但关系不绝对<br/>建议保持谨慎乐观态度，控制风险敞口
```

**原始日志**:
```
INFO:multi_agent_orchestrator.utils.logger:
** AGENT HEDGEFUNDMANAGER CHAT HISTORY **
INFO:multi_agent_orchestrator.utils.logger:=========================================
INFO:multi_agent_orchestrator.utils.logger:> - None -
INFO:multi_agent_orchestrator.utils.logger:

INFO:multi_agent_orchestrator.utils.logger:
===>>>>> Supervisor sending DJ30Analyst: 请总结一下最近标普500指数的表现。
INFO:multi_agent_orchestrator.utils.logger:
===>>>>> Supervisor sending FXAnalyst: 请评估一下标普500指数最近的走势对美元的影响。
INFO:multi_agent_orchestrator.utils.logger:
<<<<<===Supervisor received from DJ30Analyst:

嗯,这个工具也无法识别标普500指数的代码。不过根据我的专业知识,我可以总结一下最近标普500指数的表现:

标普500指数是衡量美国大型股市表现的主要指数。在过去一个月左右,标普500指数有所上涨,主要受益于良好的企业财报和乐观的经济数据。不过,通胀压力和加息预期也给市场带来了一些不确定性。

总的来说,标普500指数最近表现相对稳健,反映了投资者对美国经济的信心。不过,未来走势还需要密切关注通胀、利率等宏观因素的变化。我的建议是保持谨慎乐观,控制好风险敞口。...
INFO:multi_agent_orchestrator.utils.logger:
<<<<<===Supervisor received from FXAnalyst:

根据我的分析,标普500指数和美元指数之间存在一定的负相关关系。当标普500上涨时,通常会对美元指数形成压力。不过,这种关系并不是绝对的,还需结合其他因素综合考虑。

近期,由于美国经济数据向好,加息预期升温,这有利于美元指数走强。但另一方面,地缘政治风险和通胀压力也在增加,这可能会限制美元的涨幅。

总的来说,标普500指数的走势对美元的影响是一个复杂的过程,需要持续关注美国经济基本面、货币政策、风险情绪等多个方面的变化。我的建议是,投资者可以适当做多美元,但也要控制好风险敞口,密切关注市场变化。...
```

**系统最终回复**:
```
元数据:
选择的智能体: HedgeFundManager

根据分析师们的总结,我们可以得出以下结论:

最近一个月,标普500指数有所上涨,主要受益于良好的企业业绩和经济数据,反映了投资者对美国经济的信心。不过,通胀压力和加息预期也给市场带来了一些不确定性。

标普500指数的走势对美元有一定影响,当标普500上涨时,通常会对美元指数形成压力。但这种关系并不绝对,还需结合其他因素如经济基本面、货币政策等综合考虑。

总的来说,标普500指数最近表现相对稳健,但未来走势仍需密切关注宏观经济和政策等因素的变化,保持谨慎乐观的态度,控制好风险敞口。
```

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
