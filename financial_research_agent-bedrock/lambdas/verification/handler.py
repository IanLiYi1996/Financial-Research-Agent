import json
from typing import Dict, Any

# 导入共享模块
from models import VerificationResult
from utils import invoke_bedrock_model, parse_json_string, format_response

# 验证提示模板
VERIFICATION_PROMPT = """
你是一位细致的审计员。你收到了一份金融分析报告。你的工作是验证报告内部是否一致，来源是否清晰，以及是否存在无根据的声明。
请指出任何问题或不确定之处。

报告内容:
{report}

请评估这份报告的准确性和一致性，并以JSON格式返回结果:
```json
{{
  "verified": true或false,
  "issues": "如果verified为false，描述主要问题"
}}
```

如果报告看起来合理、一致且有根据，则verified为true，issues为空字符串。
如果发现问题，则verified为false，并在issues中详细说明问题。
"""


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    验证Lambda函数处理程序
    
    Args:
        event: Lambda事件
        context: Lambda上下文
        
    Returns:
        验证结果
    """
    try:
        # 获取报告
        report = event.get('report', '')
        
        if not report:
            return format_response(400, {"error": "缺少报告参数"})
        
        print("验证报告...")
        
        # 调用Bedrock模型验证报告
        prompt = VERIFICATION_PROMPT.format(report=report)
        response = invoke_bedrock_model(
            prompt=prompt,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            max_tokens=1000,
            temperature=0.2
        )
        
        print("模型响应:", response)
        
        # 解析JSON响应
        try:
            result = parse_json_string(response)
            
            # 验证必要的字段
            verified = result.get('verified', False)
            issues = result.get('issues', '')
            
            # 创建验证结果
            verification_result = VerificationResult(
                verified=verified,
                issues=issues
            )
            
            return verification_result.model_dump()
        
        except Exception as e:
            print(f"解析模型响应时出错: {str(e)}")
            
            # 尝试手动解析响应
            verified = "没有发现问题" in response or "No issues found" in response
            issues = response if not verified else ""
            
            # 创建验证结果
            verification_result = VerificationResult(
                verified=verified,
                issues=issues
            )
            
            return verification_result.model_dump()
    
    except Exception as e:
        print(f"处理请求时出错: {str(e)}")
        return {"error": str(e)}
