from typing import Any, Dict, List
import sys, asyncio, uuid
import os
import re
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

# 导入自定义工具和会议系统
from tools import (
    technical_indicator_analysis, 
    market_dynamics_annotation, 
    news_analysis,
    technical_indicator_description,
    market_dynamics_description,
    news_analysis_description
)
from memory import HedgeAgentMemorySystem, initialize_memory_system
from conferences import (
    budget_allocation_conference_prompt,
    experience_sharing_conference_prompt,
    extreme_market_conference_prompt,
    get_conference_prompt
)
from conference_manager import ConferenceManager

# 创建记忆系统
memory_system = HedgeAgentMemorySystem()

# 导入工具处理程序
from tools import tool_handler

# 存储正在进行的会议
active_conferences = {}

# 创建比特币分析师
bitcoin_analyst = BedrockLLMAgent(BedrockLLMAgentOptions(
    name="BitcoinAnalyst",
    description="专门分析比特币市场的专家，擅长加密货币技术分析和市场趋势预测",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    streaming=True,
    tool_config={
        'tool': technical_indicator_description + market_dynamics_description + news_analysis_description,
        'toolMaxRecursions': 5,
        'useToolHandler': lambda response, conversation: tool_handler("bedrock", response, conversation)
    }
))

bitcoin_analyst.set_system_prompt("""
你是Dave，一位专业的比特币分析师。你的职责是分析比特币市场并提供专业见解。

你的专业领域包括：
1. 比特币技术分析
2. 加密货币市场趋势
3. 区块链技术发展
4. 加密货币监管环境

在分析过程中，你应该：
- 使用技术指标分析工具评估市场状况
- 使用市场动态注释工具识别市场趋势
- 使用新闻分析工具了解市场情绪
- 基于分析结果提供买入/卖出/持有建议
- 评估风险水平并提出风险管理策略

你的分析应该客观、基于数据，并考虑当前市场环境。
""")

# 创建DJ30分析师
dj30_analyst = BedrockLLMAgent(BedrockLLMAgentOptions(
    name="DJ30Analyst",
    description="专门分析道琼斯30指数的专家，擅长股票市场分析和宏观经济趋势",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    streaming=True,
    tool_config={
        'tool': technical_indicator_description + market_dynamics_description + news_analysis_description,
        'toolMaxRecursions': 5,
        'useToolHandler': lambda response, conversation: tool_handler("bedrock", response, conversation)
    }
))

dj30_analyst.set_system_prompt("""
你是Bob，一位专业的道琼斯30指数分析师。你的职责是分析DJ30指数及其成分股，并提供专业见解。

你的专业领域包括：
1. 股票技术分析
2. 宏观经济趋势分析
3. 公司基本面分析
4. 行业发展趋势

在分析过程中，你应该：
- 使用技术指标分析工具评估市场状况
- 使用市场动态注释工具识别市场趋势
- 使用新闻分析工具了解市场情绪
- 基于分析结果提供买入/卖出/持有建议
- 评估风险水平并提出风险管理策略

你的分析应该客观、基于数据，并考虑当前市场环境和宏观经济因素。
""")

# 创建外汇分析师
fx_analyst = BedrockLLMAgent(BedrockLLMAgentOptions(
    name="FXAnalyst",
    description="专门分析外汇市场的专家，擅长货币对分析和国际经济形势评估",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    streaming=True,
    tool_config={
        'tool': technical_indicator_description + market_dynamics_description + news_analysis_description,
        'toolMaxRecursions': 5,
        'useToolHandler': lambda response, conversation: tool_handler("bedrock", response, conversation)
    }
))

fx_analyst.set_system_prompt("""
你是Emily，一位专业的外汇分析师。你的职责是分析外汇市场和主要货币对，并提供专业见解。

你的专业领域包括：
1. 外汇技术分析
2. 国际经济形势评估
3. 央行政策分析
4. 地缘政治风险评估

在分析过程中，你应该：
- 使用技术指标分析工具评估市场状况
- 使用市场动态注释工具识别市场趋势
- 使用新闻分析工具了解市场情绪
- 基于分析结果提供买入/卖出/持有建议
- 评估风险水平并提出风险管理策略

你的分析应该客观、基于数据，并考虑当前国际经济环境和地缘政治因素。
""")

# 创建对冲基金经理（主导智能体）
lead_agent = BedrockLLMAgent(BedrockLLMAgentOptions(
    name="HedgeFundManager",
    description="对冲基金经理，负责协调分析师团队并做出最终投资决策",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    streaming=True
))

# 设置对冲基金经理的系统提示
lead_agent.set_system_prompt("""
你是Otto，一位经验丰富的对冲基金经理。你的职责是协调分析师团队，整合他们的分析结果，并做出最终投资决策。

你管理着一个由三位专业分析师组成的团队：
1. Dave - 比特币分析师
2. Bob - 道琼斯30指数分析师
3. Emily - 外汇分析师

你需要根据情况召开三种类型的会议：

1. 预算分配会议：
   - 评估每个资产类别的表现
   - 分析当前市场状况
   - 确定风险水平
   - 分配投资预算到不同资产类别

2. 经验分享会议：
   - 分享过去投资决策的经验
   - 讨论成功和失败的案例
   - 更新团队的一般经验记忆
   - 提炼投资智慧

3. 极端市场会议：
   - 分析当前极端市场情况
   - 评估持仓风险
   - 讨论损失原因
   - 规划资产处置
   - 制定应对措施

在做出决策时，你应该：
- 整合各位分析师的专业意见
- 考虑当前市场环境和风险水平
- 平衡短期收益和长期增长
- 制定明确的投资策略和资产配置计划

你的最终目标是最大化投资回报，同时控制风险在可接受范围内。
""")

# 创建SupervisorAgent作为对冲基金经理
hedge_fund_manager = SupervisorAgent(
    SupervisorAgentOptions(
        name="HedgeFundManager",
        description="对冲基金经理，负责协调分析师团队并做出最终投资决策",
        lead_agent=lead_agent,
        team=[bitcoin_analyst, dj30_analyst, fx_analyst],
        storage=InMemoryChatStorage(),
        trace=True,
        extra_tools=[
            AgentTool(
                name="technical_indicator_analysis",
                func=technical_indicator_analysis,
            ),
            AgentTool(
                name="market_dynamics_annotation",
                func=market_dynamics_annotation,
            ),
            AgentTool(
                name="news_analysis",
                func=news_analysis,
            ),
            AgentTool(
                name="update_market_information",
                func=memory_system.update_market_information,
            ),
            AgentTool(
                name="update_investment_reflection",
                func=memory_system.update_investment_reflection,
            ),
            AgentTool(
                name="update_general_experience",
                func=memory_system.update_general_experience,
            ),
            AgentTool(
                name="retrieve_memories",
                func=memory_system.retrieve_memories,
            )
        ]
    ))

# 检测会议请求
def detect_conference_request(user_input: str) -> tuple:
    """
    检测用户输入是否是会议请求
    
    参数:
    - user_input: 用户输入
    
    返回:
    - (是否是会议请求, 会议类型)
    """
    user_input_lower = user_input.lower()
    
    if "预算分配会议" in user_input_lower or "预算会议" in user_input_lower:
        return (True, "budget_allocation")
    elif "经验分享会议" in user_input_lower or "经验会议" in user_input_lower:
        return (True, "experience_sharing")
    elif "极端市场会议" in user_input_lower or "极端会议" in user_input_lower:
        return (True, "extreme_market")
    elif "下一轮" in user_input_lower or "继续会议" in user_input_lower:
        return (True, "next_round")
    elif "结束会议" in user_input_lower or "总结会议" in user_input_lower:
        return (True, "conclude")
    else:
        return (False, None)

async def handle_request(_orchestrator: MultiAgentOrchestrator, _user_input: str, _user_id: str, _session_id: str):
    try:
        # 检测是否是会议请求
        is_conference, conference_type = detect_conference_request(_user_input)
        
        if is_conference:
            # 处理会议请求
            if conference_type == "next_round":
                # 继续下一轮会议
                if _session_id in active_conferences:
                    conference = active_conferences[_session_id]
                    is_final = await conference.next_round(_user_id, _session_id)
                    
                    if is_final:
                        # 会议结束，获取总结
                        summary = await conference.conclude_conference(_user_id, _session_id)
                        print(f"\n\033[34m{summary}\033[0m")
                        
                        # 删除会议
                        del active_conferences[_session_id]
                    else:
                        # 会议继续
                        current_round = conference.current_round + 1
                        print(f"\n\033[34m会议进入第{current_round}轮讨论。请在讨论结束后输入\"下一轮\"继续，或\"结束会议\"来总结会议结果。\033[0m")
                else:
                    print("\n\033[34m当前没有正在进行的会议。请先召开一个会议。\033[0m")
            elif conference_type == "conclude":
                # 结束会议
                if _session_id in active_conferences:
                    conference = active_conferences[_session_id]
                    summary = await conference.conclude_conference(_user_id, _session_id)
                    print(f"\n\033[34m{summary}\033[0m")
                    
                    # 删除会议
                    del active_conferences[_session_id]
                else:
                    print("\n\033[34m当前没有正在进行的会议。请先召开一个会议。\033[0m")
            else:
                # 开始新会议
                if _session_id in active_conferences:
                    print("\n\033[34m已经有一个会议正在进行。请先结束当前会议，或输入\"下一轮\"继续当前会议。\033[0m")
                else:
                    # 创建新会议
                    conference = ConferenceManager(
                        conference_type=conference_type,
                        supervisor_agent=hedge_fund_manager,
                        team_agents=[bitcoin_analyst, dj30_analyst, fx_analyst],
                        max_rounds=3
                    )
                    
                    # 存储会议
                    active_conferences[_session_id] = conference
                    
                    # 启动会议
                    await conference.start_conference(_user_id, _session_id)
                    
                    # 使用orchestrator处理会议提示
                    prompt = get_conference_prompt(conference_type)
                    prompt += f"\n\n这是会议的第1轮讨论，请分享您的初步想法。"
                    
                    # 发送会议提示给主导智能体
                    classifier_result = ClassifierResult(selected_agent=hedge_fund_manager, confidence=1.0)
                    await _orchestrator.agent_process_request(prompt, _user_id, _session_id, classifier_result)
                    
                    print(f"\n\033[34m会议已开始，第1轮讨论正在进行。请在讨论结束后输入\"下一轮\"继续，或\"结束会议\"来总结会议结果。\033[0m")
        else:
            # 处理普通请求
            classifier_result = ClassifierResult(selected_agent=hedge_fund_manager, confidence=1.0)

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
    except Exception as e:
        print(f"\n处理请求时出错: {e}")
        import traceback
        traceback.print_exc()

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

    print(f"""欢迎使用HedgeAgents-v2多智能体系统。\n
我是Otto，您的对冲基金经理。我将协调我们的分析师团队为您提供投资建议。
我们的分析师团队包括：
- Dave: 比特币分析师，专注于加密货币市场
- Bob: 道琼斯30指数分析师，专注于股票市场
- Emily: 外汇分析师，专注于货币市场

您可以：
1. 询问特定市场的分析和建议
2. 请求召开预算分配会议
3. 请求召开经验分享会议
4. 请求召开极端市场会议
5. 获取综合投资建议

会议将进行多轮讨论，您可以通过输入\"下一轮\"继续会议，或\"结束会议\"来总结会议结果。
""")

    # 创建事件循环
    loop = asyncio.get_event_loop()
    
    async def main_loop():
        while True:
            # 获取用户输入
            user_input = input("\n您: ").strip()

            if user_input.lower() == 'quit':
                print("退出程序。再见！")
                sys.exit()

            # 运行异步函数
            if user_input is not None and user_input != '':
                await handle_request(orchestrator, user_input, USER_ID, SESSION_ID)
    
    # 运行主循环
    try:
        loop.run_until_complete(main_loop())
    except KeyboardInterrupt:
        print("\n程序已中断。再见！")
    finally:
        loop.close()
