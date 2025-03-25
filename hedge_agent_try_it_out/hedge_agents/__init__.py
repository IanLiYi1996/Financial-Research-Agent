"""
HedgeAgents - 基于multi-agent-orchestrator的对冲基金多智能体系统

这个包实现了一个对冲基金多智能体系统，包括：
1. 专业分析师智能体（比特币分析师、DJ30分析师、外汇分析师）
2. 对冲基金经理智能体（作为SupervisorAgent）
3. 市场分析工具
4. 记忆系统
5. 会议系统
"""

from .main import hedge_fund_manager
from .tools import (
    technical_indicator_analysis, 
    market_dynamics_annotation, 
    news_analysis
)
from .memory import HedgeAgentMemorySystem, initialize_memory_system
from .conferences import (
    budget_allocation_conference_prompt,
    experience_sharing_conference_prompt,
    extreme_market_conference_prompt,
    get_conference_prompt,
    get_conference_result_template
)

__version__ = "0.1.0"
