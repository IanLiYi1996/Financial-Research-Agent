import json
from typing import Dict, Any, List

# 导入共享模块
from models import FinancialReportData
from utils import invoke_bedrock_model, parse_json_string, format_response

# 报告生成提示模板
REPORT_PROMPT = """
你是一位高级金融分析师。你将获得原始查询、搜索摘要以及专家分析。
你的任务是将这些内容综合成一份长篇markdown报告（至少几个段落），包括一个简短的执行摘要和后续问题。

原始查询: {query}

搜索结果摘要:
{search_results}

基本面分析:
{fundamentals_analysis}

风险分析:
{risk_analysis}

请生成一份完整的金融分析报告，包括以下部分:
1. 执行摘要（2-3句话）
2. 详细的markdown格式报告，包括适当的标题、段落和格式
3. 3-5个后续研究问题

请以JSON格式返回结果，格式如下:
```json
{{
  "short_summary": "简短的执行摘要",
  "markdown_report": "完整的markdown报告",
  "follow_up_questions": [
    "问题1",
    "问题2",
    "问题3"
  ]
}}
```
"""


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    报告生成Lambda函数处理程序
    
    Args:
        event: Lambda事件
        context: Lambda上下文
        
    Returns:
        生成的报告
    """
    try:
        # 获取参数
        query = event.get('query', '')
        search_results = event.get('searchResults', [])
        fundamentals_analysis = event.get('fundamentalsAnalysis', '')
        risk_analysis = event.get('riskAnalysis', '')
        
        if not query:
            return format_response(400, {"error": "缺少查询参数"})
        
        print(f"生成报告: {query}")
        
        # 合并搜索结果
        combined_results = "\n\n".join(search_results) if search_results else "没有可用的搜索结果。"
        
        # 生成报告
        prompt = REPORT_PROMPT.format(
            query=query,
            search_results=combined_results,
            fundamentals_analysis=fundamentals_analysis or "没有可用的基本面分析。",
            risk_analysis=risk_analysis or "没有可用的风险分析。"
        )
        
        response = invoke_bedrock_model(
            prompt=prompt,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            max_tokens=4000,
            temperature=0.5
        )
        
        print("模型响应:", response)
        
        # 解析JSON响应
        try:
            result = parse_json_string(response)
            
            # 验证必要的字段
            short_summary = result.get('short_summary', '')
            markdown_report = result.get('markdown_report', '')
            follow_up_questions = result.get('follow_up_questions', [])
            
            # 创建报告数据
            report_data = FinancialReportData(
                short_summary=short_summary,
                markdown_report=markdown_report,
                follow_up_questions=follow_up_questions
            )
            
            return report_data.model_dump()
        
        except Exception as e:
            print(f"解析模型响应时出错: {str(e)}")
            
            # 尝试手动解析响应
            lines = response.split('\n')
            short_summary = ""
            markdown_report = response
            follow_up_questions = []
            
            # 尝试提取执行摘要
            for i, line in enumerate(lines):
                if "执行摘要" in line or "Executive Summary" in line:
                    if i + 1 < len(lines):
                        short_summary = lines[i + 1]
                        break
            
            # 尝试提取后续问题
            in_questions = False
            for line in lines:
                if "后续问题" in line or "Follow-up Questions" in line:
                    in_questions = True
                    continue
                
                if in_questions and line.strip():
                    # 移除列表标记
                    question = line.strip()
                    if question.startswith(('-', '*', '•')):
                        question = question[1:].strip()
                    elif question[0].isdigit() and '.' in question:
                        question = question.split('.', 1)[1].strip()
                    
                    if question:
                        follow_up_questions.append(question)
            
            # 如果仍然无法解析，创建一个基本的报告
            if not short_summary:
                short_summary = f"关于'{query}'的金融分析报告"
            
            if not follow_up_questions:
                follow_up_questions = [
                    f"{query}的未来增长前景如何？",
                    f"{query}面临的主要竞争挑战是什么？",
                    f"{query}的财务状况在行业中处于什么位置？"
                ]
            
            # 创建报告数据
            report_data = FinancialReportData(
                short_summary=short_summary,
                markdown_report=markdown_report,
                follow_up_questions=follow_up_questions
            )
            
            return report_data.model_dump()
    
    except Exception as e:
        print(f"处理请求时出错: {str(e)}")
        return {"error": str(e)}
