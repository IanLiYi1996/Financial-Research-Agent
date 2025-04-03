"""
RAG Agents工具系统

实现以下工具：
1. 知识库检索工具
2. 输入验证工具
3. 回答生成工具
"""

from typing import Dict, List, Any, Optional
import asyncio
import json
import random
from datetime import datetime

# 知识库检索工具描述
knowledge_base_search_description = [{
    "toolSpec": {
        "name": "knowledge_base_search",
        "description": "搜索知识库，检索与查询相关的内容",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用户查询内容"
                    },
                    "top_k": {
                        "type": "number",
                        "description": "返回的结果数量，默认为3"
                    }
                },
                "required": ["query"]
            }
        }
    }
}]

# 输入验证工具描述
input_validation_description = [{
    "toolSpec": {
        "name": "input_validation",
        "description": "验证用户输入是否满足要求",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用户查询内容"
                    },
                    "requirements": {
                        "type": "array",
                        "description": "输入需要满足的要求列表"
                    }
                },
                "required": ["query"]
            }
        }
    }
}]

# 回答生成工具描述
answer_generation_description = [{
    "toolSpec": {
        "name": "answer_generation",
        "description": "基于检索结果生成回答",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用户查询内容"
                    },
                    "retrieval_results": {
                        "type": "array",
                        "description": "检索结果列表"
                    }
                },
                "required": ["query", "retrieval_results"]
            }
        }
    }
}]

# 模拟知识库数据
knowledge_base = {
    "AWS": [
        {
            "id": "aws-001",
            "title": "AWS 行业解决方案概述",
            "content": "AWS提供针对不同行业的解决方案，包括金融服务、医疗健康、零售、媒体娱乐等。这些解决方案结合了AWS的云服务和行业专业知识，帮助企业解决特定行业的挑战。",
            "category": "general",
            "industry": "all"
        },
        {
            "id": "aws-002",
            "title": "AWS 金融服务行业解决方案",
            "content": "AWS金融服务行业解决方案帮助银行、保险、支付和资本市场企业提高运营效率、降低成本、加速创新并提升客户体验。主要解决方案领域包括风险管理、支付处理、欺诈检测和合规性。",
            "category": "industry",
            "industry": "FSI"
        },
        {
            "id": "aws-003",
            "title": "AWS 医疗健康行业解决方案",
            "content": "AWS医疗健康行业解决方案帮助医疗服务提供商、生命科学组织和健康保险公司改善患者护理、加速研发并提高运营效率。主要解决方案领域包括医疗数据分析、临床系统现代化和医疗研究。",
            "category": "industry",
            "industry": "LSHC"
        },
        {
            "id": "aws-004",
            "title": "AWS 零售行业解决方案",
            "content": "AWS零售行业解决方案帮助零售商优化运营、提升客户体验并推动创新。主要解决方案领域包括全渠道零售、供应链优化、个性化营销和客户分析。",
            "category": "industry",
            "industry": "RCH"
        },
        {
            "id": "aws-005",
            "title": "AWS 媒体娱乐行业解决方案",
            "content": "AWS媒体娱乐行业解决方案帮助媒体公司、内容创作者和分发商创建、交付和货币化内容。主要解决方案领域包括内容制作、媒体供应链、内容分发和直播。",
            "category": "industry",
            "industry": "MEAD"
        },
        {
            "id": "aws-006",
            "title": "AWS 游戏行业解决方案",
            "content": "AWS游戏行业解决方案帮助游戏开发商和发行商构建、运营和扩展游戏。主要解决方案领域包括游戏服务器托管、游戏分析、实时多人游戏和游戏AI。",
            "category": "industry",
            "industry": "Game"
        },
        {
            "id": "aws-007",
            "title": "AWS 汽车行业解决方案",
            "content": "AWS汽车行业解决方案帮助汽车制造商、供应商和出行服务提供商加速创新并提高运营效率。主要解决方案领域包括互联汽车、自动驾驶、数字化制造和供应链优化。",
            "category": "industry",
            "industry": "AUTO"
        },
        {
            "id": "aws-008",
            "title": "AWS 制造业解决方案",
            "content": "AWS制造业解决方案帮助制造商优化生产流程、提高质量控制并实现数字化转型。主要解决方案领域包括工业物联网、预测性维护、智能工厂和供应链可见性。",
            "category": "industry",
            "industry": "MFG"
        },
        {
            "id": "aws-009",
            "title": "AWS 金融服务风险管理解决方案",
            "content": "AWS金融服务风险管理解决方案帮助金融机构评估、监控和管理各种风险，包括市场风险、信用风险和运营风险。该解决方案利用AWS的高性能计算和机器学习服务，实现更准确的风险建模和更快的风险计算。",
            "category": "solution_area",
            "industry": "FSI",
            "solution_area": "风险管理"
        },
        {
            "id": "aws-010",
            "title": "AWS 金融服务支付处理解决方案",
            "content": "AWS金融服务支付处理解决方案帮助支付服务提供商构建安全、可扩展和高性能的支付系统。该解决方案利用AWS的全球基础设施和安全服务，实现跨地区的支付处理和欺诈检测。",
            "category": "solution_area",
            "industry": "FSI",
            "solution_area": "支付处理"
        }
    ]
}

# 工具处理程序
async def tool_handler(response, conversation):
    """
    处理工具调用
    
    参数:
    - response: 响应
    - conversation: 对话历史
    
    返回:
    - 工具调用结果
    """
    from multi_agent_orchestrator.types import ConversationMessage, ParticipantRole
    
    response_content_blocks = response.content
    
    # 初始化空的工具结果列表
    tool_results = []
    
    if not response_content_blocks:
        raise ValueError("No content blocks in response")
    
    for content_block in response_content_blocks:
        if "text" in content_block:
            # 处理文本内容（如果需要）
            pass
        
        if "toolUse" in content_block:
            tool_use_block = content_block["toolUse"]
            tool_use_name = tool_use_block.get("name")
            
            if tool_use_name == "knowledge_base_search":
                tool_response = await knowledge_base_search(
                    tool_use_block["input"].get("query", ""),
                    tool_use_block["input"].get("top_k", 3)
                )
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_block["toolUseId"],
                        "content": [{"text": tool_response}],
                    }
                })
            elif tool_use_name == "input_validation":
                tool_response = await input_validation(
                    tool_use_block["input"].get("query", ""),
                    tool_use_block["input"].get("requirements", [])
                )
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_block["toolUseId"],
                        "content": [{"text": tool_response}],
                    }
                })
            elif tool_use_name == "answer_generation":
                tool_response = await answer_generation(
                    tool_use_block["input"].get("query", ""),
                    tool_use_block["input"].get("retrieval_results", [])
                )
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_block["toolUseId"],
                        "content": [{"text": tool_response}],
                    }
                })
    
    # 将工具结果嵌入到新的用户消息中
    message = ConversationMessage(
        role=ParticipantRole.USER.value,
        content=tool_results
    )
    
    return message

# 知识库检索工具
async def knowledge_base_search(query: str, top_k: int = 3) -> str:
    """
    搜索知识库，检索与查询相关的内容
    
    参数:
    - query: 用户查询内容
    - top_k: 返回的结果数量，默认为3
    
    返回:
    - 检索结果（字符串格式）
    """
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    # 简单的关键词匹配搜索
    results = []
    query_lower = query.lower()
    
    # 搜索所有知识库
    for category, documents in knowledge_base.items():
        for doc in documents:
            # 检查标题和内容是否包含查询关键词
            if query_lower in doc["title"].lower() or query_lower in doc["content"].lower():
                results.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "content": doc["content"],
                    "category": doc.get("category", "unknown"),
                    "industry": doc.get("industry", "unknown"),
                    "solution_area": doc.get("solution_area", "unknown"),
                    "relevance_score": calculate_relevance_score(query, doc)
                })
    
    # 按相关性得分排序
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # 限制结果数量
    results = results[:top_k]
    
    if not results:
        return f"""
知识库检索结果
时间戳: {datetime.now().isoformat()}
查询: {query}

未找到相关内容。
"""
    
    # 构建结果字符串
    result_str = f"""
知识库检索结果
时间戳: {datetime.now().isoformat()}
查询: {query}
结果数量: {len(results)}

"""
    
    for i, result in enumerate(results, 1):
        result_str += f"""
结果 {i}:
标题: {result['title']}
相关性得分: {result['relevance_score']:.2f}
类别: {result['category']}
行业: {result['industry']}
{f"解决方案领域: {result['solution_area']}" if result['solution_area'] != "unknown" else ""}
内容: {result['content']}
"""
    
    return result_str

# 输入验证工具
async def input_validation(query: str, requirements: List[str] = None) -> str:
    """
    验证用户输入是否满足要求
    
    参数:
    - query: 用户查询内容
    - requirements: 输入需要满足的要求列表
    
    返回:
    - 验证结果（字符串格式）
    """
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    if not requirements:
        requirements = [
            "查询应明确指定行业",
            "查询应包含具体问题或需求"
        ]
    
    # 验证查询是否满足要求
    validation_results = []
    is_valid = True
    
    # 检查查询长度
    if len(query.strip()) < 5:
        validation_results.append({
            "requirement": "查询长度应大于5个字符",
            "is_satisfied": False,
            "feedback": "查询过短，请提供更详细的信息"
        })
        is_valid = False
    
    # 检查是否指定行业
    industries = ["金融", "医疗", "零售", "媒体", "游戏", "汽车", "制造"]
    has_industry = any(industry in query for industry in industries)
    if not has_industry:
        validation_results.append({
            "requirement": "查询应明确指定行业",
            "is_satisfied": False,
            "feedback": "未指定行业，请明确您关注的行业，如金融、医疗、零售等"
        })
        is_valid = False
    else:
        validation_results.append({
            "requirement": "查询应明确指定行业",
            "is_satisfied": True,
            "feedback": "已指定行业"
        })
    
    # 检查是否包含具体问题或需求
    question_keywords = ["如何", "什么", "为什么", "怎样", "是否", "能否", "?", "？"]
    has_question = any(keyword in query for keyword in question_keywords)
    if not has_question:
        validation_results.append({
            "requirement": "查询应包含具体问题或需求",
            "is_satisfied": False,
            "feedback": "未包含具体问题或需求，请明确您想了解的内容"
        })
        is_valid = False
    else:
        validation_results.append({
            "requirement": "查询应包含具体问题或需求",
            "is_satisfied": True,
            "feedback": "已包含具体问题或需求"
        })
    
    # 构建结果字符串
    result_str = f"""
输入验证结果
时间戳: {datetime.now().isoformat()}
查询: {query}
是否有效: {is_valid}

验证详情:
"""
    
    for result in validation_results:
        result_str += f"- {result['requirement']}: {'✓' if result['is_satisfied'] else '✗'} ({result['feedback']})\n"
    
    if not is_valid:
        result_str += "\n改进建议:\n"
        for result in validation_results:
            if not result["is_satisfied"]:
                result_str += f"- {result['feedback']}\n"
    
    return result_str

# 回答生成工具
async def answer_generation(query: str, retrieval_results: List[Dict[str, Any]]) -> str:
    """
    基于检索结果生成回答
    
    参数:
    - query: 用户查询内容
    - retrieval_results: 检索结果列表
    
    返回:
    - 生成的回答（字符串格式）
    """
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    if not retrieval_results:
        return f"""
回答生成结果
时间戳: {datetime.now().isoformat()}
查询: {query}

很抱歉，我没有找到与您查询相关的信息。请尝试重新表述您的问题，或者提供更多细节。
"""
    
    # 提取相关内容
    contents = [result.get("content", "") for result in retrieval_results]
    combined_content = " ".join(contents)
    
    # 简单的回答生成逻辑
    answer = f"根据检索到的信息，{combined_content[:200]}..."
    
    # 构建结果字符串
    result_str = f"""
回答生成结果
时间戳: {datetime.now().isoformat()}
查询: {query}
检索结果数量: {len(retrieval_results)}

生成的回答:
{answer}

参考来源:
"""
    
    for i, result in enumerate(retrieval_results, 1):
        result_str += f"{i}. {result.get('title', 'Unknown Title')} (ID: {result.get('id', 'Unknown ID')})\n"
    
    return result_str

# 辅助函数：计算相关性得分
def calculate_relevance_score(query: str, document: Dict[str, Any]) -> float:
    """
    计算查询与文档的相关性得分
    
    参数:
    - query: 用户查询内容
    - document: 文档
    
    返回:
    - 相关性得分
    """
    query_lower = query.lower()
    title_lower = document["title"].lower()
    content_lower = document["content"].lower()
    
    # 计算标题匹配得分
    title_score = 0
    if query_lower in title_lower:
        title_score = 0.6
    else:
        # 计算查询中有多少词出现在标题中
        query_words = query_lower.split()
        matching_words = sum(1 for word in query_words if word in title_lower)
        title_score = 0.4 * (matching_words / max(1, len(query_words)))
    
    # 计算内容匹配得分
    content_score = 0
    if query_lower in content_lower:
        content_score = 0.4
    else:
        # 计算查询中有多少词出现在内容中
        query_words = query_lower.split()
        matching_words = sum(1 for word in query_words if word in content_lower)
        content_score = 0.3 * (matching_words / max(1, len(query_words)))
    
    # 计算总得分
    total_score = title_score + content_score
    
    # 添加类别和行业匹配的额外得分
    if "category" in document and document["category"] in query_lower:
        total_score += 0.1
    
    if "industry" in document and document["industry"] in query_lower:
        total_score += 0.1
    
    if "solution_area" in document and document["solution_area"] != "unknown" and document["solution_area"] in query_lower:
        total_score += 0.2
    
    return min(1.0, total_score)  # 确保得分不超过1.0
