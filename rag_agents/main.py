"""
RAG Agents主程序

实现SupervisorAgent和主程序逻辑
"""

from typing import Dict, List, Any
import sys, asyncio, uuid
import os
import json

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

# 导入自定义智能体和工具
from .agents import create_input_verifier_agent, create_rag_agent
from .tools import (
    knowledge_base_search,
    input_validation,
    answer_generation,
    tool_handler
)
from .memory import RAGMemorySystem, initialize_memory_system

# 创建记忆系统
memory_system = RAGMemorySystem()

# 包装异步函数的同步函数
def update_query_history_wrapper(query_id: str, query: str, is_valid: bool = None) -> str:
    """
    包装update_query_history异步函数的同步函数
    
    参数:
    - query_id: 查询ID
    - query: 用户查询内容
    - is_valid: 查询是否有效
    
    返回:
    - 序列化后的结果字符串
    """
    # 创建一个新的事件循环
    loop = asyncio.new_event_loop()
    try:
        # 在新的事件循环中运行异步函数
        result = loop.run_until_complete(memory_system.update_query_history(query_id, query, is_valid))
        # 将结果序列化为JSON字符串
        return json.dumps(result)
    finally:
        # 关闭事件循环
        loop.close()

def update_retrieval_results_wrapper(query_id: str, results: List[Dict[str, Any]]) -> str:
    """
    包装update_retrieval_results异步函数的同步函数
    
    参数:
    - query_id: 查询ID
    - results: 检索结果列表
    
    返回:
    - 序列化后的结果字符串
    """
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(memory_system.update_retrieval_results(query_id, results))
        return json.dumps(result)
    finally:
        loop.close()

def update_verification_results_wrapper(query_id: str, is_valid: bool, feedback: str = None) -> str:
    """
    包装update_verification_results异步函数的同步函数
    
    参数:
    - query_id: 查询ID
    - is_valid: 查询是否有效
    - feedback: 验证反馈
    
    返回:
    - 序列化后的结果字符串
    """
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(memory_system.update_verification_results(query_id, is_valid, feedback))
        return json.dumps(result)
    finally:
        loop.close()

def get_query_context_wrapper(query_id: str) -> str:
    """
    包装get_query_context异步函数的同步函数
    
    参数:
    - query_id: 查询ID
    
    返回:
    - 序列化后的结果字符串
    """
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(memory_system.get_query_context(query_id))
        return json.dumps(result)
    finally:
        loop.close()

# 创建主导智能体（SupervisorAgent）
def create_supervisor_agent(model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0") -> SupervisorAgent:
    """
    创建主导智能体（SupervisorAgent）
    
    参数:
    - model_id: 使用的模型ID
    
    返回:
    - SupervisorAgent
    """
    # 创建输入检查智能体
    input_verifier = create_input_verifier_agent(model_id)
    
    # 创建RAG智能体
    rag_agent = create_rag_agent(model_id)
    
    # 创建主导智能体
    lead_agent = BedrockLLMAgent(BedrockLLMAgentOptions(
        name="SupervisorAgent",
        description="主导智能体，负责协调输入检查智能体和RAG智能体",
        model_id=model_id,
        streaming=True
    ))
    
    # 设置主导智能体的系统提示
    lead_agent.set_system_prompt("""
你是一个RAG系统的主导智能体，负责协调输入检查智能体和RAG智能体的工作。

你管理着一个由两位专业智能体组成的团队：
1. InputVerifierAgent - 输入检查智能体，负责检查用户输入是否满足要求
2. RAGAgent - RAG智能体，负责检索知识库并生成回答

你的主要职责包括：
1. 接收用户查询
2. 将查询发送给输入检查智能体进行验证
3. 根据验证结果决定后续操作：
   - 如果输入有效，将查询发送给RAG智能体生成回答
   - 如果输入无效，将验证结果返回给用户，要求用户提供更多信息
4. 整合各智能体的输出，生成最终回复

工作流程：
1. 接收用户查询
2. 将查询发送给InputVerifierAgent进行验证
3. 分析验证结果：
   - 如果输入有效，将查询发送给RAGAgent生成回答
   - 如果输入无效，将验证结果和改进建议返回给用户
4. 如果用户提供了新的输入，重复步骤2-3
5. 如果RAGAgent生成了回答，将回答返回给用户

注意事项：
- 你的回复应该简洁明了，重点突出
- 不要编造不存在的信息，如果知识库中没有相关内容，应诚实告知
- 确保用户查询满足要求后再进行知识库检索和回答生成
- 在整个过程中保持对话的连贯性和上下文理解
""")
    
    # 创建SupervisorAgent
    supervisor = SupervisorAgent(
        SupervisorAgentOptions(
            name="SupervisorAgent",
            description="主导智能体，负责协调输入检查智能体和RAG智能体",
            lead_agent=lead_agent,
            team=[input_verifier, rag_agent],
            storage=InMemoryChatStorage(),
            trace=True,
            extra_tools=[
                AgentTool(
                    name="update_query_history",
                    func=update_query_history_wrapper,
                ),
                AgentTool(
                    name="update_retrieval_results",
                    func=update_retrieval_results_wrapper,
                ),
                AgentTool(
                    name="update_verification_results",
                    func=update_verification_results_wrapper,
                ),
                AgentTool(
                    name="get_query_context",
                    func=get_query_context_wrapper,
                )
            ]
        ))
    
    return supervisor

# 创建主导智能体实例
rag_supervisor = create_supervisor_agent()

async def handle_request(_orchestrator: MultiAgentOrchestrator, _user_input: str, _user_id: str, _session_id: str):
    """
    处理用户请求
    
    参数:
    - _orchestrator: 多智能体协调器
    - _user_input: 用户输入
    - _user_id: 用户ID
    - _session_id: 会话ID
    """
    classifier_result = ClassifierResult(selected_agent=rag_supervisor, confidence=1.0)

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

async def main():
    """主程序入口"""
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

    print(f"""欢迎使用RAG Agents多智能体系统。\n
我是RAG系统的主导智能体，负责协调输入检查智能体和RAG智能体的工作。
我们的智能体团队包括：
- InputVerifierAgent: 输入检查智能体，负责检查用户输入是否满足要求
- RAGAgent: RAG智能体，负责检索知识库并生成回答

您可以向我提问关于AWS行业解决方案的问题，例如：
1. 金融行业的AWS解决方案有哪些？
2. AWS如何帮助零售行业实现数字化转型？
3. 游戏行业使用AWS有哪些优势？
""")

    while True:
        # 获取用户输入
        user_input = input("\n您: ").strip()

        if user_input.lower() in ['quit', 'exit', '退出']:
            print("退出程序。再见！")
            sys.exit()

        # 运行异步函数
        if user_input is not None and user_input != '':
            await handle_request(orchestrator, user_input, USER_ID, SESSION_ID)

if __name__ == "__main__":
    asyncio.run(main())
