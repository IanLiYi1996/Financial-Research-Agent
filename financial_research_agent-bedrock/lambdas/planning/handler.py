import json
from typing import Dict, Any, List

# 导入共享模块
from models import FinancialSearchItem, FinancialSearchPlan
from utils import invoke_bedrock_model, parse_json_string, format_response

# 规划提示模板
PLANNING_PROMPT = """
你是一个金融研究规划者。给定一个金融分析请求，生成一组网络搜索以收集所需的背景信息。
目标是获取最近的新闻、财报电话会议或10-K摘要、分析师评论和行业背景。

请为以下查询生成5到15个搜索词：

{query}

请以JSON格式返回结果，格式如下：
```json
{{
  "searches": [
    {{
      "reason": "搜索原因1",
      "query": "搜索词1"
    }},
    {{
      "reason": "搜索原因2",
      "query": "搜索词2"
    }}
    // 更多搜索项...
  ]
}}
```

确保每个搜索项都包含明确的原因和具体的搜索词。搜索词应该是具体的，可以直接用于网络搜索。
"""


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    规划Lambda函数处理程序
    
    Args:
        event: Lambda事件
        context: Lambda上下文
        
    Returns:
        搜索计划
    """
    try:
        # 获取查询
        query = event.get('query', '')
        if not query:
            return format_response(400, {"error": "缺少查询参数"})
        
        print(f"生成搜索计划: {query}")
        
        # 调用Bedrock模型生成搜索计划
        prompt = PLANNING_PROMPT.format(query=query)
        response = invoke_bedrock_model(
            prompt=prompt,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            max_tokens=2000,
            temperature=0.2
        )
        
        print("模型响应:", response)
        
        # 解析JSON响应
        try:
            result = parse_json_string(response)
            searches = result.get('searches', [])
            
            # 验证搜索项
            validated_searches: List[Dict[str, str]] = []
            for search in searches:
                if 'reason' in search and 'query' in search:
                    validated_searches.append({
                        'reason': search['reason'],
                        'query': search['query']
                    })
            
            # 创建搜索计划
            search_plan = FinancialSearchPlan(searches=[
                FinancialSearchItem(**search) for search in validated_searches
            ])
            
            return search_plan.model_dump()
        
        except Exception as e:
            print(f"解析模型响应时出错: {str(e)}")
            
            # 尝试手动解析响应
            searches = []
            lines = response.split('\n')
            current_reason = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('"reason":') or line.startswith('reason:'):
                    current_reason = line.split(':', 1)[1].strip().strip('"').strip(',').strip('"')
                elif line.startswith('"query":') or line.startswith('query:'):
                    if current_reason:
                        query_text = line.split(':', 1)[1].strip().strip('"').strip(',').strip('"')
                        searches.append({
                            'reason': current_reason,
                            'query': query_text
                        })
                        current_reason = None
            
            # 如果仍然无法解析，创建一个基本的搜索计划
            if not searches:
                searches = [
                    {
                        'reason': '获取最新财务信息',
                        'query': f"{query} 最新财务报告"
                    },
                    {
                        'reason': '获取行业背景',
                        'query': f"{query} 行业分析"
                    },
                    {
                        'reason': '获取分析师评论',
                        'query': f"{query} 分析师评价"
                    }
                ]
            
            # 创建搜索计划
            search_plan = FinancialSearchPlan(searches=[
                FinancialSearchItem(**search) for search in searches
            ])
            
            return search_plan.model_dump()
    
    except Exception as e:
        print(f"处理请求时出错: {str(e)}")
        return {"error": str(e)}
