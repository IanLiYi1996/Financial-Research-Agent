import json
import boto3
import os
from typing import Any, Dict, List, Optional

# 初始化Bedrock客户端
bedrock_runtime = boto3.client('bedrock-runtime')
bedrock_agent = boto3.client('bedrock-agent-runtime')


def invoke_bedrock_model(
    prompt: str,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None
) -> str:
    """
    调用Bedrock模型生成文本
    
    Args:
        prompt: 用户提示
        model_id: 模型ID
        max_tokens: 最大生成令牌数
        temperature: 温度参数
        system_prompt: 系统提示（可选）
        
    Returns:
        生成的文本
    """
    # 根据模型类型构建请求体
    if model_id.startswith("anthropic.claude"):
        # Claude模型
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        if system_prompt:
            request_body["system"] = system_prompt
    
    elif model_id.startswith("amazon.titan"):
        # Titan模型
        request_body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "stopSequences": []
            }
        }
    
    else:
        raise ValueError(f"不支持的模型ID: {model_id}")
    
    # 调用模型
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body),
        contentType='application/json'
    )
    
    # 解析响应
    response_body = json.loads(response['body'].read())
    
    # 根据模型类型提取生成的文本
    if model_id.startswith("anthropic.claude"):
        return response_body['content'][0]['text']
    elif model_id.startswith("amazon.titan"):
        return response_body['results'][0]['outputText']
    else:
        raise ValueError(f"不支持的模型ID: {model_id}")


def retrieve_from_knowledge_base(
    query: str,
    knowledge_base_id: str,
    number_of_results: int = 3
) -> List[str]:
    """
    从知识库中检索信息
    
    Args:
        query: 检索查询
        knowledge_base_id: 知识库ID
        number_of_results: 返回结果数量
        
    Returns:
        检索到的文本列表
    """
    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=knowledge_base_id,
            retrievalQuery={
                'text': query
            },
            numberOfResults=number_of_results
        )
        
        return [result['content']['text'] for result in response['retrievalResults']]
    except Exception as e:
        print(f"从知识库检索失败: {str(e)}")
        return []


def parse_json_string(json_string: str) -> Dict[str, Any]:
    """
    解析JSON字符串
    
    Args:
        json_string: JSON字符串
        
    Returns:
        解析后的字典
    """
    # 查找JSON内容的开始和结束位置
    start_idx = json_string.find('{')
    end_idx = json_string.rfind('}') + 1
    
    if start_idx == -1 or end_idx == 0:
        raise ValueError("无法在字符串中找到有效的JSON")
    
    # 提取JSON内容
    json_content = json_string[start_idx:end_idx]
    
    try:
        return json.loads(json_content)
    except json.JSONDecodeError:
        # 尝试修复常见的JSON格式问题
        # 1. 将单引号替换为双引号
        json_content = json_content.replace("'", '"')
        # 2. 确保布尔值和null是小写的
        json_content = json_content.replace("True", "true").replace("False", "false").replace("None", "null")
        
        try:
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {str(e)}")


def format_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化API响应
    
    Args:
        status_code: HTTP状态码
        body: 响应体
        
    Returns:
        格式化的响应
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body": json.dumps(body)
    }
