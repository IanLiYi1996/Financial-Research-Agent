"""
RAG Agents智能体定义

实现以下智能体：
1. 输入检查智能体（InputVerifierAgent）
2. RAG智能体（RAGAgent）
"""

from typing import Dict, List, Any, Optional
from multi_agent_orchestrator.agents import (
    BedrockLLMAgent, BedrockLLMAgentOptions,
    AgentResponse
)

from tools import (
    knowledge_base_search_description,
    input_validation_description,
    answer_generation_description,
    tool_handler
)

# 创建输入检查智能体
def create_input_verifier_agent(model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0") -> BedrockLLMAgent:
    """
    创建输入检查智能体
    
    参数:
    - model_id: 使用的模型ID
    
    返回:
    - 输入检查智能体
    """
    input_verifier = BedrockLLMAgent(BedrockLLMAgentOptions(
        name="InputVerifierAgent",
        description="负责检查用户输入是否满足要求，并提供改进建议",
        model_id=model_id,
        streaming=True,
        tool_config={
            'tool': knowledge_base_search_description + input_validation_description,
            'toolMaxRecursions': 5,
            'useToolHandler': tool_handler
        }
    ))
    
    # 设置系统提示
    input_verifier.set_system_prompt("""
你是一个输入检查智能体，负责检查用户输入是否满足要求，并提供改进建议。

你的主要职责包括：
1. 检查用户输入是否满足以下要求：
   - 查询长度应大于5个字符
   - 查询应明确指定行业（如金融、医疗、零售、媒体、游戏、汽车、制造等）
   - 查询应包含具体问题或需求（如"如何"、"什么"、"为什么"等）

2. 当用户输入不满足要求时：
   - 使用知识库检索工具获取相关信息
   - 基于检索结果提供具体的改进建议
   - 明确告知用户需要补充哪些信息

3. 当用户输入满足要求时：
   - 确认输入有效
   - 简要总结用户查询的主要内容和意图

你可以使用以下工具：
- knowledge_base_search：搜索知识库，检索与查询相关的内容
- input_validation：验证用户输入是否满足要求

工作流程：
1. 接收用户输入
2. 使用input_validation工具验证输入
3. 如果输入无效，使用knowledge_base_search工具获取相关信息
4. 基于验证结果和检索结果，提供反馈和建议
5. 如果输入有效，确认并总结查询内容

注意事项：
- 你的回复应该简洁明了，重点突出
- 当提供改进建议时，应具体明确，避免模糊表述
- 不要编造不存在的信息，如果知识库中没有相关内容，应诚实告知
""")
    
    return input_verifier

# 创建RAG智能体
def create_rag_agent(model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0") -> BedrockLLMAgent:
    """
    创建RAG智能体
    
    参数:
    - model_id: 使用的模型ID
    
    返回:
    - RAG智能体
    """
    rag_agent = BedrockLLMAgent(BedrockLLMAgentOptions(
        name="RAGAgent",
        description="负责检索知识库并生成回答",
        model_id=model_id,
        streaming=True,
        tool_config={
            'tool': knowledge_base_search_description + answer_generation_description,
            'toolMaxRecursions': 5,
            'useToolHandler': tool_handler
        }
    ))
    
    # 设置系统提示
    rag_agent.set_system_prompt("""
你是一个RAG（检索增强生成）智能体，负责检索知识库并生成回答。

你的主要职责包括：
1. 接收经过验证的用户查询
2. 使用知识库检索工具获取相关信息
3. 基于检索结果生成准确、全面的回答
4. 当知识库中没有相关信息时，诚实告知用户

你可以使用以下工具：
- knowledge_base_search：搜索知识库，检索与查询相关的内容
- answer_generation：基于检索结果生成回答

工作流程：
1. 接收用户查询
2. 使用knowledge_base_search工具检索相关信息
3. 分析检索结果的相关性和完整性
4. 如果检索结果充分，使用answer_generation工具生成回答
5. 如果检索结果不充分，告知用户知识库中缺乏相关信息

回答格式要求：
1. 回答应直接针对用户查询
2. 内容应基于检索结果，不要编造信息
3. 结构应清晰，重点突出
4. 如有必要，可以使用列表、表格等格式增强可读性
5. 引用检索结果的来源

注意事项：
- 不要编造不存在的信息，如果知识库中没有相关内容，应诚实告知
- 回答应尽可能全面，但也要简洁明了
- 如果检索结果包含多个相关但不同的信息点，应综合整理后呈现
- 优先使用检索结果中相关性最高的信息
""")
    
    return rag_agent
