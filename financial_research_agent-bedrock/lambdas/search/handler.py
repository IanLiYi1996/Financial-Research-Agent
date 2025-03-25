import json
import os
import requests
from typing import Dict, Any, List, Optional
import boto3

# 导入共享模块
from utils import invoke_bedrock_model, retrieve_from_knowledge_base, format_response

# 搜索API配置
SEARCH_API_KEY = os.environ.get('SEARCH_API_KEY', '')
SEARCH_ENGINE_ID = os.environ.get('SEARCH_ENGINE_ID', '')

# 知识库配置
KNOWLEDGE_BASE_ID = os.environ.get('KNOWLEDGE_BASE_ID', '')

# 搜索摘要提示模板
SEARCH_SUMMARY_PROMPT = """
你是一个专注于金融主题的研究助手。给定一个搜索词和搜索结果，请提供一个最多300字的简短摘要。
重点关注对金融分析师有用的关键数字、事件或引述。

搜索词: {search_term}
搜索原因: {reason}

搜索结果:
{search_results}

请提供一个简洁的摘要，重点关注与金融分析相关的关键信息。
"""


def perform_web_search(query: str, max_results: int = 5) -> List[str]:
    """
    执行网络搜索
    
    Args:
        query: 搜索查询
        max_results: 最大结果数
        
    Returns:
        搜索结果列表
    """
    if not SEARCH_API_KEY or not SEARCH_ENGINE_ID:
        print("搜索API密钥或搜索引擎ID未配置，跳过网络搜索")
        return []
    
    try:
        # 使用Google Custom Search API
        url = f"https://www.googleapis.com/customsearch/v1?key={SEARCH_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
        response = requests.get(url)
        results = response.json().get('items', [])
        
        # 提取标题和摘要
        search_results = []
        for item in results[:max_results]:
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            link = item.get('link', '')
            search_results.append(f"标题: {title}\n摘要: {snippet}\n链接: {link}")
        
        return search_results
    
    except Exception as e:
        print(f"执行网络搜索时出错: {str(e)}")
        return []


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    搜索Lambda函数处理程序
    
    Args:
        event: Lambda事件
        context: Lambda上下文
        
    Returns:
        搜索摘要
    """
    try:
        # 获取搜索参数
        search_term = event.get('searchTerm', '')
        reason = event.get('reason', '')
        
        if not search_term:
            return format_response(400, {"error": "缺少搜索词参数"})
        
        print(f"执行搜索: {search_term}")
        
        # 从知识库检索信息
        kb_results = []
        if KNOWLEDGE_BASE_ID:
            kb_results = retrieve_from_knowledge_base(
                query=search_term,
                knowledge_base_id=KNOWLEDGE_BASE_ID,
                number_of_results=3
            )
            print(f"从知识库检索到{len(kb_results)}个结果")
        
        # 执行网络搜索
        web_results = perform_web_search(search_term)
        print(f"从网络搜索到{len(web_results)}个结果")
        
        # 合并结果
        all_results = kb_results + web_results
        
        # 如果没有结果，返回空摘要
        if not all_results:
            return {"summary": f"未找到与'{search_term}'相关的信息。"}
        
        # 使用Bedrock模型总结结果
        combined_results = "\n\n".join(all_results)
        prompt = SEARCH_SUMMARY_PROMPT.format(
            search_term=search_term,
            reason=reason,
            search_results=combined_results
        )
        
        summary = invoke_bedrock_model(
            prompt=prompt,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            max_tokens=500,
            temperature=0.2
        )
        
        return {"summary": summary}
    
    except Exception as e:
        print(f"处理请求时出错: {str(e)}")
        return {"error": str(e)}
