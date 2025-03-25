import json
import boto3
import os
from typing import Dict, Any

# 导入共享模块
from models import ResearchRequest, ResearchResponse
from utils import format_response

# 初始化Lambda客户端
lambda_client = boto3.client('lambda')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    主协调Lambda函数处理程序
    
    Args:
        event: API Gateway事件
        context: Lambda上下文
        
    Returns:
        API Gateway响应
    """
    try:
        # 解析请求
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        request = ResearchRequest(**body)
        query = request.query
        
        print(f"收到研究请求: {query}")
        
        # 步骤1: 规划搜索
        planning_response = lambda_client.invoke(
            FunctionName=os.environ['PLANNING_LAMBDA'],
            InvocationType='RequestResponse',
            Payload=json.dumps({
                "query": query
            })
        )
        
        planning_result = json.loads(planning_response['Payload'].read())
        searches = planning_result.get('searches', [])
        
        print(f"生成了{len(searches)}个搜索项")
        
        # 步骤2: 执行搜索
        search_results = []
        for search_item in searches:
            search_response = lambda_client.invoke(
                FunctionName=os.environ['SEARCH_LAMBDA'],
                InvocationType='RequestResponse',
                Payload=json.dumps({
                    "searchTerm": search_item['query'],
                    "reason": search_item['reason']
                })
            )
            
            search_result = json.loads(search_response['Payload'].read())
            if 'summary' in search_result:
                search_results.append(search_result['summary'])
        
        print(f"完成了{len(search_results)}个搜索")
        
        # 步骤3: 执行分析
        analysis_response = lambda_client.invoke(
            FunctionName=os.environ['ANALYSIS_LAMBDA'],
            InvocationType='RequestResponse',
            Payload=json.dumps({
                "query": query,
                "searchResults": search_results
            })
        )
        
        analysis_result = json.loads(analysis_response['Payload'].read())
        fundamentals_analysis = analysis_result.get('fundamentals', '')
        risk_analysis = analysis_result.get('risks', '')
        
        print("完成了基本面和风险分析")
        
        # 步骤4: 生成报告
        report_response = lambda_client.invoke(
            FunctionName=os.environ['REPORT_LAMBDA'],
            InvocationType='RequestResponse',
            Payload=json.dumps({
                "query": query,
                "searchResults": search_results,
                "fundamentalsAnalysis": fundamentals_analysis,
                "riskAnalysis": risk_analysis
            })
        )
        
        report_result = json.loads(report_response['Payload'].read())
        
        print("生成了报告")
        
        # 步骤5: 验证报告
        verification_response = lambda_client.invoke(
            FunctionName=os.environ['VERIFICATION_LAMBDA'],
            InvocationType='RequestResponse',
            Payload=json.dumps({
                "report": report_result['markdownReport']
            })
        )
        
        verification_result = json.loads(verification_response['Payload'].read())
        
        print("完成了报告验证")
        
        # 构建响应
        response = ResearchResponse(
            report=report_result,
            verification=verification_result
        )
        
        return format_response(200, response.model_dump())
    
    except Exception as e:
        print(f"处理请求时出错: {str(e)}")
        return format_response(500, {"error": str(e)})
