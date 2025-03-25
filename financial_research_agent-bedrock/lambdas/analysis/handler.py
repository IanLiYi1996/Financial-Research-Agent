import json
from typing import Dict, Any, List

# 导入共享模块
from models import AnalysisSummary
from utils import invoke_bedrock_model, format_response

# 财务分析提示模板
FINANCIALS_PROMPT = """
你是一个专注于公司基本面的金融分析师，关注收入、利润、利润率和增长轨迹等指标。
根据提供的搜索结果，对公司的近期财务表现进行简明分析。提取关键指标或引述。
保持在2段以内。

原始查询: {query}

搜索结果:
{search_results}

请提供一个关注财务基本面的简明分析。
"""

# 风险分析提示模板
RISK_PROMPT = """
你是一个风险分析师，专注于识别公司前景中的潜在风险因素。
根据提供的背景研究，对风险因素进行简短分析，如竞争威胁、监管问题、供应链问题或增长放缓等。
保持在2段以内。

原始查询: {query}

搜索结果:
{search_results}

请提供一个关注潜在风险的简明分析。
"""


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    分析Lambda函数处理程序
    
    Args:
        event: Lambda事件
        context: Lambda上下文
        
    Returns:
        分析结果
    """
    try:
        # 获取参数
        query = event.get('query', '')
        search_results = event.get('searchResults', [])
        
        if not query:
            return format_response(400, {"error": "缺少查询参数"})
        
        if not search_results:
            return {
                "fundamentals": "没有足够的信息进行基本面分析。",
                "risks": "没有足够的信息进行风险分析。"
            }
        
        print(f"执行分析: {query}")
        
        # 合并搜索结果
        combined_results = "\n\n".join(search_results)
        
        # 执行基本面分析
        fundamentals_prompt = FINANCIALS_PROMPT.format(
            query=query,
            search_results=combined_results
        )
        
        fundamentals_analysis = invoke_bedrock_model(
            prompt=fundamentals_prompt,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            max_tokens=500,
            temperature=0.2
        )
        
        print("完成基本面分析")
        
        # 执行风险分析
        risk_prompt = RISK_PROMPT.format(
            query=query,
            search_results=combined_results
        )
        
        risk_analysis = invoke_bedrock_model(
            prompt=risk_prompt,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            max_tokens=500,
            temperature=0.2
        )
        
        print("完成风险分析")
        
        return {
            "fundamentals": fundamentals_analysis,
            "risks": risk_analysis
        }
    
    except Exception as e:
        print(f"处理请求时出错: {str(e)}")
        return {"error": str(e)}
