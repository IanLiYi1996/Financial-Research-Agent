from typing import Any, Dict, List
import sys, asyncio, uuid
import os
from datetime import datetime, timezone
from multi_agent_orchestrator.utils import Logger
from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator, OrchestratorConfig
from multi_agent_orchestrator.agents import (
    BedrockLLMAgent, BedrockLLMAgentOptions,
    AgentResponse,
    SupervisorAgent, SupervisorAgentOptions
)
from multi_agent_orchestrator.classifiers import ClassifierResult
from multi_agent_orchestrator.types import ConversationMessage
from multi_agent_orchestrator.storage import InMemoryChatStorage
from multi_agent_orchestrator.utils import AgentTool

# 导入自定义工具和内存系统
from tools import (
    query_nebula_knowledge_graph,
    query_opensearch_knowledge,
    query_dynamodb_user_info,
    update_dynamodb_user_info,
    search_financial_info,
    nebula_description,
    opensearch_description,
    dynamodb_description,
    search_description
)
from memory import FundAdvisorMemorySystem

# 创建记忆系统
memory_system = FundAdvisorMemorySystem()

# 导入工具处理程序
from tools import tool_handler

# 创建用户风险分析师
risk_analyst = BedrockLLMAgent(BedrockLLMAgentOptions(
    name="RiskAnalyst",
    description="专门分析用户风险偏好的专家，负责评估用户的风险承受能力",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    streaming=True,
    tool_config={
        'tool': dynamodb_description,
        'toolMaxRecursions': 5,
        'useToolHandler': tool_handler
    }
))

risk_analyst.set_system_prompt("""
你是一位专业的用户风险分析师。你的职责是分析用户的风险偏好和承受能力，为用户提供合适的风险评估。

你的专业领域包括：
1. 用户风险偏好评估
2. 风险承受能力分析
3. 用户基本信息管理
4. 风险等级划分

在分析过程中，你应该：
- 使用DynamoDB工具查询用户的基本信息
- 根据用户的年龄、收入、投资经验等因素评估风险承受能力
- 将用户的风险偏好分为保守型、稳健型、平衡型、成长型、进取型五个等级
- 将用户的基本信息和风险偏好存储到DynamoDB中
- 提供风险评估结果和建议

你的分析应该客观、专业，并考虑用户的实际情况。
""")

# 创建检索问答专家
knowledge_expert = BedrockLLMAgent(BedrockLLMAgentOptions(
    name="KnowledgeExpert",
    description="专门负责金融知识检索和问答的专家",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    streaming=True,
    tool_config={
        'tool': opensearch_description + search_description,
        'toolMaxRecursions': 5,
        'useToolHandler': tool_handler
    }
))

knowledge_expert.set_system_prompt("""
你是一位专业的金融知识专家。你的职责是回答用户关于金融和基金投资的问题，提供准确的金融知识。

你的专业领域包括：
1. 基金产品知识
2. 金融市场分析
3. 投资策略解读
4. 金融术语解释

在回答问题时，你应该：
- 使用OpenSearch工具检索金融知识库
- 必要时使用搜索工具获取最新的金融信息
- 提供准确、客观的金融知识
- 解释复杂的金融概念，使其易于理解
- 避免提供具体的投资建议，而是提供知识和教育

你的回答应该专业、准确，并基于可靠的金融知识。
""")

# 创建基金推荐专家
fund_recommender = BedrockLLMAgent(BedrockLLMAgentOptions(
    name="FundRecommender",
    description="专门负责基金推荐的专家，根据用户需求和风险偏好推荐合适的基金产品",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    streaming=True,
    tool_config={
        'tool': nebula_description + dynamodb_description,
        'toolMaxRecursions': 5,
        'useToolHandler': tool_handler
    }
))

fund_recommender.set_system_prompt("""
你是一位专业的基金推荐专家。你的职责是根据用户的需求和风险偏好，推荐合适的基金产品。

你的专业领域包括：
1. 基金产品分析
2. 投资组合构建
3. 风险收益匹配
4. 基金筛选和评估

在推荐基金时，你应该：
- 使用DynamoDB工具查询用户的基本信息和风险偏好
- 根据用户的风险偏好和投资需求，生成查询知识图谱的SQL语句
- 使用Nebula工具查询基金知识图谱，获取符合条件的基金产品
- 分析基金的历史表现、风险指标和投资策略
- 推荐最适合用户的基金产品组合
- 解释推荐理由和预期收益风险

你的推荐应该客观、专业，并考虑用户的实际需求和风险承受能力。
""")

# 创建投资顾问（主导智能体）
lead_agent = BedrockLLMAgent(BedrockLLMAgentOptions(
    name="InvestmentAdvisor",
    description="投资顾问，负责协调分析师团队并为用户提供综合投资建议",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    streaming=True
))

# 设置投资顾问的系统提示
lead_agent.set_system_prompt("""
你是一位专业的投资顾问。你的职责是协调分析师团队，整合他们的分析结果，并为用户提供综合投资建议。

你管理着一个由三位专业分析师组成的团队：
1. 风险分析师 - 负责评估用户的风险偏好和承受能力
2. 知识专家 - 负责回答用户关于金融和基金投资的问题
3. 基金推荐专家 - 负责根据用户需求和风险偏好推荐合适的基金产品

你需要根据用户的输入，判断用户的意图，并调用相应的专家：
1. 如果用户询问关于自己风险偏好的问题，或需要更新个人信息，调用风险分析师
2. 如果用户询问金融知识或基金概念，调用知识专家
3. 如果用户需要基金推荐或投资建议，调用基金推荐专家

在与用户交流时，你应该：
- 理解用户的真实需求和意图
- 协调各位专家的工作，确保他们提供的信息准确且相关
- 整合各位专家的分析结果，提供全面的投资建议
- 使用专业但易于理解的语言与用户沟通
- 确保建议符合用户的风险偏好和投资目标

你的最终目标是帮助用户做出明智的投资决策，提供专业、客观的投资建议。
""")

# 创建SupervisorAgent作为投资顾问
investment_advisor = SupervisorAgent(
    SupervisorAgentOptions(
        name="InvestmentAdvisor",
        description="投资顾问，负责协调分析师团队并为用户提供综合投资建议",
        lead_agent=lead_agent,
        team=[risk_analyst, knowledge_expert, fund_recommender],
        storage=InMemoryChatStorage(),
        trace=True,
        extra_tools=[
            AgentTool(
                name="query_nebula_knowledge_graph",
                func=query_nebula_knowledge_graph,
            ),
            AgentTool(
                name="query_opensearch_knowledge",
                func=query_opensearch_knowledge,
            ),
            AgentTool(
                name="query_dynamodb_user_info",
                func=query_dynamodb_user_info,
            ),
            AgentTool(
                name="update_dynamodb_user_info",
                func=update_dynamodb_user_info,
            ),
            AgentTool(
                name="search_financial_info",
                func=search_financial_info,
            ),
            AgentTool(
                name="update_user_profile",
                func=memory_system.update_user_profile,
            ),
            AgentTool(
                name="update_fund_knowledge",
                func=memory_system.update_fund_knowledge,
            ),
            AgentTool(
                name="update_interaction_history",
                func=memory_system.update_interaction_history,
            ),
            AgentTool(
                name="retrieve_memories",
                func=memory_system.retrieve_memories,
            )
        ]
    ))

async def handle_request(_orchestrator: MultiAgentOrchestrator, _user_input: str, _user_id: str, _session_id: str):
    classifier_result = ClassifierResult(selected_agent=investment_advisor, confidence=1.0)

    response: AgentResponse = await _orchestrator.agent_process_request(_user_input, _user_id, _session_id, classifier_result)

    # 打印元数据
    print("\n元数据:")
    print(f"选择的智能体: {response.metadata.agent_name}")
    
    # 处理响应
    if isinstance(response, AgentResponse) and response.streaming is False:
        # 处理常规响应
        if isinstance(response.output, str):
            print(f"\033[34m{response.output}\033[0m")
        elif isinstance(response.output, ConversationMessage):
            print(f"\033[34m{response.output.content[0].get('text')}\033[0m")
    else:
        # 处理流式响应
        print("\n响应:")
        async for chunk in response.output:
            if hasattr(chunk, 'text'):
                print(chunk.text, end='', flush=True)
            else:
                print(chunk, end='', flush=True)
        print()

if __name__ == "__main__":
    # 初始化orchestrator
    orchestrator = MultiAgentOrchestrator(options=OrchestratorConfig(
        LOG_AGENT_CHAT=True,
        LOG_CLASSIFIER_CHAT=True,
        LOG_CLASSIFIER_RAW_OUTPUT=True,
        LOG_CLASSIFIER_OUTPUT=True,
        LOG_EXECUTION_TIMES=True,
        MAX_RETRIES=3,
        USE_DEFAULT_AGENT_IF_NONE_IDENTIFIED=True,
        MAX_MESSAGE_PAIRS_PER_AGENT=10,
    ),
    storage=InMemoryChatStorage()
    )

    USER_ID = str(uuid.uuid4())
    SESSION_ID = str(uuid.uuid4())

    print(f"""欢迎使用基金投顾多智能体系统。\n
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
""")

    while True:
        # 获取用户输入
        user_input = input("\n您: ").strip()

        if user_input.lower() == 'quit':
            print("退出程序。再见！")
            sys.exit()

        # 运行异步函数
        if user_input is not None and user_input != '':
            asyncio.run(handle_request(orchestrator, user_input, USER_ID, SESSION_ID))
