# Financial Research Agent - Jupyter实现

本项目是Financial Research Agent的简化版本，使用AWS Bedrock API实现，可以在本地通过Jupyter Notebook或Python脚本运行。

## 项目结构

```
financial_research_agent-jupyter/
├── README.md                     # 项目说明文档
├── financial_research_agent.ipynb # Jupyter Notebook实现
├── financial_research_agent.py   # Python脚本实现
└── requirements.txt              # 依赖库
```

## 功能特点

1. **模块化设计**：将金融研究流程拆分为规划、搜索、分析、报告生成和验证等模块
2. **AWS Bedrock集成**：使用AWS Bedrock的Claude模型进行自然语言处理
3. **本地运行**：无需部署到AWS云端，可以在本地环境中运行
4. **简单易用**：提供Jupyter Notebook和Python脚本两种使用方式

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置AWS凭证

在使用本项目前，您需要配置AWS凭证，并确保有权访问AWS Bedrock服务。

1. 安装AWS CLI
2. 配置AWS凭证

```bash
aws configure
# 输入您的AWS Access Key ID、Secret Access Key、默认区域和输出格式
```

3. 确保您的AWS账户已启用Bedrock服务，并有权访问Claude模型

## 使用方法

### 方法1：使用Python脚本

```bash
python financial_research_agent.py
```

运行脚本后，按照提示输入您的金融研究查询，例如："分析苹果公司最近一个季度的表现"。

### 方法2：使用Jupyter Notebook

1. 启动Jupyter Notebook

```bash
jupyter notebook
```

2. 打开`financial_research_agent.ipynb`文件
3. 按顺序运行各个单元格
4. 在最后一个单元格中输入您的查询

## 工作流程

1. **规划搜索**：根据用户查询生成一组搜索策略
2. **执行搜索**：执行网络搜索并总结结果（当前使用模拟数据）
3. **执行分析**：对搜索结果进行财务基本面分析和风险分析
4. **生成报告**：综合分析结果生成详细的金融分析报告
5. **验证报告**：验证报告的准确性和一致性

## 自定义配置

您可以通过修改`financial_research_agent.py`文件中的以下参数来自定义配置：

- `region`：AWS区域
- `TEXT_MODEL_ID`：使用的Bedrock文本模型ID
- `EMBEDDING_MODEL_ID`：使用的Bedrock嵌入模型ID

## 扩展功能

要扩展本项目的功能，您可以：

1. **实现真实的搜索API**：替换`perform_web_search`方法中的模拟数据，使用真实的搜索API（如Google Custom Search API）
2. **添加数据可视化**：在报告中添加图表和可视化内容
3. **集成金融数据API**：接入Yahoo Finance、Alpha Vantage等金融数据API
4. **添加历史查询记录**：保存用户的查询历史和生成的报告

## 与AWS Bedrock版本的区别

与完整的AWS Bedrock版本相比，本Jupyter实现有以下区别：

1. **本地运行**：无需部署到AWS云端，可以在本地环境中运行
2. **简化架构**：不使用Lambda函数和API Gateway
3. **模拟搜索**：使用模拟数据代替真实的搜索API
4. **单一进程**：所有功能在同一个进程中执行，而不是分布式架构

## 注意事项

1. 使用AWS Bedrock API会产生费用，请注意控制使用量
2. 本项目仅用于演示和学习目的，不建议用于生产环境
3. 当前的搜索功能使用模拟数据，实际应用中需要替换为真实的搜索API
