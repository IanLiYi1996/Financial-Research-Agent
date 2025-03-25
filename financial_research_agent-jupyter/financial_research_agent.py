#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版Financial Research Agent - Python实现

本脚本实现了一个简化版的Financial Research Agent，使用AWS Bedrock API。
这个简化版本包含基本的功能，如规划搜索、执行搜索、分析、生成报告和验证。
"""

import boto3
import json
import os
import requests
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


# 数据模型定义
class FinancialSearchItem(BaseModel):
    """搜索项定义"""
    reason: str
    query: str


class FinancialSearchPlan(BaseModel):
    """搜索计划定义"""
    searches: List[FinancialSearchItem]


class FinancialReportData(BaseModel):
    """金融报告数据定义"""
    short_summary: str
    markdown_report: str
    follow_up_questions: List[str]


class VerificationResult(BaseModel):
    """验证结果定义"""
    verified: bool
    issues: str


class FinancialResearchAgent:
    """金融研究代理"""

    def __init__(self, region="us-east-1"):
        """初始化金融研究代理"""
        # 配置AWS区域
        self.region = region

        # 创建Bedrock客户端
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)

        # 配置模型ID
        self.TEXT_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"  # Claude 3 Sonnet
        self.EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v1"  # Titan Embedding

    def invoke_bedrock_model(
        self,
        prompt: str,
        model_id: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """调用Bedrock模型生成文本"""
        if model_id is None:
            model_id = self.TEXT_MODEL_ID

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
        response = self.bedrock_runtime.invoke_model(
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

    def parse_json_string(self, json_string: str) -> Dict[str, Any]:
        """解析JSON字符串"""
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

    def perform_web_search(self, query: str, max_results: int = 5) -> List[str]:
        """执行网络搜索（示例实现，需要替换为实际的搜索API）"""
        # 这里应该使用实际的搜索API，如Google Custom Search API
        # 为了演示，我们返回一些模拟的搜索结果
        return [
            f"模拟搜索结果1: 关于{query}的信息",
            f"模拟搜索结果2: {query}的最新动态",
            f"模拟搜索结果3: {query}的分析报告"
        ]

    def plan_searches(self, query: str) -> FinancialSearchPlan:
        """规划搜索策略"""
        print("规划搜索策略...")
        
        # 规划提示模板
        planning_prompt = """
        你是一个金融研究规划者。给定一个金融分析请求，生成一组网络搜索以收集所需的背景信息。
        目标是获取最近的新闻、财报电话会议或10-K摘要、分析师评论和行业背景。

        请为以下查询生成5到10个搜索词：

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
        
        # 调用Bedrock模型生成搜索计划
        prompt = planning_prompt.format(query=query)
        response = self.invoke_bedrock_model(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.2
        )
        
        # 解析JSON响应
        try:
            result = self.parse_json_string(response)
            searches = result.get('searches', [])
            
            # 创建搜索计划
            search_items = [FinancialSearchItem(**search) for search in searches]
            search_plan = FinancialSearchPlan(searches=search_items)
            
            return search_plan
        
        except Exception as e:
            print(f"解析搜索计划失败: {str(e)}")
            # 创建一个基本的搜索计划
            searches = [
                FinancialSearchItem(reason='获取最新财务信息', query=f"{query} 最新财务报告"),
                FinancialSearchItem(reason='获取行业背景', query=f"{query} 行业分析"),
                FinancialSearchItem(reason='获取分析师评论', query=f"{query} 分析师评价")
            ]
            return FinancialSearchPlan(searches=searches)

    def execute_searches(self, search_plan: FinancialSearchPlan) -> List[str]:
        """执行搜索"""
        print(f"执行{len(search_plan.searches)}个搜索...")
        
        search_results = []
        for i, search_item in enumerate(search_plan.searches):
            print(f"  搜索 {i+1}/{len(search_plan.searches)}: {search_item.query}")
            
            # 执行网络搜索
            raw_results = self.perform_web_search(search_item.query)
            
            # 搜索摘要提示模板
            summary_prompt = """
            你是一个专注于金融主题的研究助手。给定一个搜索词和搜索结果，请提供一个最多300字的简短摘要。
            重点关注对金融分析师有用的关键数字、事件或引述。

            搜索词: {search_term}
            搜索原因: {reason}

            搜索结果:
            {search_results}

            请提供一个简洁的摘要，重点关注与金融分析相关的关键信息。
            """
            
            # 调用Bedrock模型总结搜索结果
            prompt = summary_prompt.format(
                search_term=search_item.query,
                reason=search_item.reason,
                search_results="\n\n".join(raw_results)
            )
            
            summary = self.invoke_bedrock_model(
                prompt=prompt,
                max_tokens=500,
                temperature=0.2
            )
            
            search_results.append(summary)
        
        return search_results

    def perform_analysis(self, query: str, search_results: List[str]) -> Dict[str, str]:
        """执行财务分析和风险分析"""
        print("执行分析...")
        
        # 合并搜索结果
        combined_results = "\n\n".join(search_results)
        
        # 财务分析提示模板
        financials_prompt = """
        你是一个专注于公司基本面的金融分析师，关注收入、利润、利润率和增长轨迹等指标。
        根据提供的搜索结果，对公司的近期财务表现进行简明分析。提取关键指标或引述。
        保持在2段以内。

        原始查询: {query}

        搜索结果:
        {search_results}

        请提供一个关注财务基本面的简明分析。
        """
        
        # 风险分析提示模板
        risk_prompt = """
        你是一个风险分析师，专注于识别公司前景中的潜在风险因素。
        根据提供的背景研究，对风险因素进行简短分析，如竞争威胁、监管问题、供应链问题或增长放缓等。
        保持在2段以内。

        原始查询: {query}

        搜索结果:
        {search_results}

        请提供一个关注潜在风险的简明分析。
        """
        
        # 执行基本面分析
        print("  执行基本面分析...")
        fundamentals_prompt = financials_prompt.format(
            query=query,
            search_results=combined_results
        )
        
        fundamentals_analysis = self.invoke_bedrock_model(
            prompt=fundamentals_prompt,
            max_tokens=500,
            temperature=0.2
        )
        
        # 执行风险分析
        print("  执行风险分析...")
        risk_prompt = risk_prompt.format(
            query=query,
            search_results=combined_results
        )
        
        risk_analysis = self.invoke_bedrock_model(
            prompt=risk_prompt,
            max_tokens=500,
            temperature=0.2
        )
        
        return {
            "fundamentals": fundamentals_analysis,
            "risks": risk_analysis
        }

    def generate_report(self, query: str, search_results: List[str], analysis_results: Dict[str, str]) -> FinancialReportData:
        """生成报告"""
        print("生成报告...")
        
        # 报告生成提示模板
        report_prompt = """
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
        
        # 调用Bedrock模型生成报告
        prompt = report_prompt.format(
            query=query,
            search_results="\n\n".join(search_results),
            fundamentals_analysis=analysis_results.get("fundamentals", ""),
            risk_analysis=analysis_results.get("risks", "")
        )
        
        response = self.invoke_bedrock_model(
            prompt=prompt,
            max_tokens=4000,
            temperature=0.5
        )
        
        # 解析JSON响应
        try:
            result = self.parse_json_string(response)
            
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
            
            return report_data
        
        except Exception as e:
            print(f"解析报告失败: {str(e)}")
            # 创建一个基本的报告
            return FinancialReportData(
                short_summary=f"关于'{query}'的金融分析报告",
                markdown_report=response,
                follow_up_questions=[
                    f"{query}的未来增长前景如何？",
                    f"{query}面临的主要竞争挑战是什么？",
                    f"{query}的财务状况在行业中处于什么位置？"
                ]
            )

    def verify_report(self, report: str) -> VerificationResult:
        """验证报告"""
        print("验证报告...")
        
        # 验证提示模板
        verification_prompt = """
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
        
        # 调用Bedrock模型验证报告
        prompt = verification_prompt.format(report=report)
        response = self.invoke_bedrock_model(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.2
        )
        
        # 解析JSON响应
        try:
            result = self.parse_json_string(response)
            
            # 验证必要的字段
            verified = result.get('verified', False)
            issues = result.get('issues', '')
            
            # 创建验证结果
            verification_result = VerificationResult(
                verified=verified,
                issues=issues
            )
            
            return verification_result
        
        except Exception as e:
            print(f"解析验证结果失败: {str(e)}")
            # 创建一个基本的验证结果
            verified = "没有发现问题" in response or "No issues found" in response
            issues = response if not verified else ""
            
            return VerificationResult(
                verified=verified,
                issues=issues
            )

    def run(self, query: str) -> Dict[str, Any]:
        """执行金融研究流程"""
        print(f"开始处理查询: {query}")
        start_time = time.time()
        
        # 步骤1: 规划搜索
        search_plan = self.plan_searches(query)
        
        # 步骤2: 执行搜索
        search_results = self.execute_searches(search_plan)
        
        # 步骤3: 执行分析
        analysis_results = self.perform_analysis(query, search_results)
        
        # 步骤4: 生成报告
        report_data = self.generate_report(query, search_results, analysis_results)
        
        # 步骤5: 验证报告
        verification_result = self.verify_report(report_data.markdown_report)
        
        # 计算执行时间
        execution_time = time.time() - start_time
        print(f"处理完成，耗时: {execution_time:.2f}秒")
        
        # 返回结果
        return {
            "report": report_data.model_dump(),
            "verification": verification_result.model_dump(),
            "execution_time": execution_time
        }


def display_report(result: Dict[str, Any]) -> None:
    """显示报告结果"""
    report = result["report"]
    verification = result["verification"]
    execution_time = result["execution_time"]
    
    print("\n" + "="*80)
    print("执行摘要:")
    print("-"*80)
    print(report["short_summary"])
    
    print("\n" + "="*80)
    print("详细报告:")
    print("-"*80)
    print(report["markdown_report"])
    
    print("\n" + "="*80)
    print("后续问题:")
    print("-"*80)
    for i, question in enumerate(report["follow_up_questions"], 1):
        print(f"{i}. {question}")
    
    print("\n" + "="*80)
    print("验证结果:")
    print("-"*80)
    if verification["verified"]:
        print("✓ 报告已验证")
    else:
        print("⚠ 验证问题:")
        print(verification["issues"])
    
    print("\n" + "="*80)
    print(f"处理时间: {execution_time:.2f}秒")
    print("="*80)


def main():
    """主函数"""
    # 创建金融研究代理
    agent = FinancialResearchAgent()
    
    # 获取用户查询
    print("欢迎使用金融研究助手!")
    print("请输入您的金融研究查询（例如：'分析苹果公司最近一个季度的表现'）:")
    query = input("> ")
    
    # 执行研究
    result = agent.run(query)
    
    # 显示结果
    display_report(result)


if __name__ == "__main__":
    main()
