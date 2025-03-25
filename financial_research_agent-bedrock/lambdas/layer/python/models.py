from typing import List, Optional
from pydantic import BaseModel


class FinancialSearchItem(BaseModel):
    """搜索项定义"""
    reason: str
    """搜索原因"""
    
    query: str
    """搜索查询"""


class FinancialSearchPlan(BaseModel):
    """搜索计划定义"""
    searches: List[FinancialSearchItem]
    """搜索项列表"""


class AnalysisSummary(BaseModel):
    """分析摘要定义"""
    summary: str
    """分析摘要内容"""


class FinancialReportData(BaseModel):
    """金融报告数据定义"""
    short_summary: str
    """简短的执行摘要"""
    
    markdown_report: str
    """完整的Markdown报告"""
    
    follow_up_questions: List[str]
    """后续研究问题"""


class VerificationResult(BaseModel):
    """验证结果定义"""
    verified: bool
    """报告是否通过验证"""
    
    issues: str
    """如果未通过验证，描述主要问题"""


class ResearchRequest(BaseModel):
    """研究请求定义"""
    query: str
    """用户查询"""


class ResearchResponse(BaseModel):
    """研究响应定义"""
    report: FinancialReportData
    """生成的报告"""
    
    verification: VerificationResult
    """验证结果"""
