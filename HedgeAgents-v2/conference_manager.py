"""
HedgeAgents-v2会议管理系统

实现多轮会议的管理和流程控制
"""

from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
from multi_agent_orchestrator.agents import SupervisorAgent, BedrockLLMAgent
from multi_agent_orchestrator.types import ConversationMessage, ParticipantRole
from multi_agent_orchestrator.orchestrator import MultiAgentOrchestrator
from multi_agent_orchestrator.classifiers import ClassifierResult
from conferences import get_conference_prompt, get_conference_result_template

class ConferenceManager:
    """
    会议管理类，用于管理多轮会议的流程
    """
    
    def __init__(self, conference_type: str, supervisor_agent: SupervisorAgent, team_agents: List[BedrockLLMAgent], max_rounds: int = 3):
        """
        初始化会议管理器
        
        参数:
        - conference_type: 会议类型，可以是"budget_allocation"、"experience_sharing"或"extreme_market"
        - supervisor_agent: 主持人智能体（对冲基金经理）
        - team_agents: 团队成员智能体列表（分析师）
        - max_rounds: 最大会议轮次
        """
        self.conference_type = conference_type
        self.supervisor_agent = supervisor_agent
        self.team_agents = team_agents
        self.max_rounds = max_rounds
        self.current_round = 0
        self.discussion_history = []
        self.is_completed = False
        self.conference_id = f"{conference_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
    async def start_conference(self, user_id: str, session_id: str) -> str:
        """
        启动会议
        
        参数:
        - user_id: 用户ID
        - session_id: 会话ID
        
        返回:
        - 会议初始提示
        """
        # 获取会议提示
        prompt = get_conference_prompt(self.conference_type)
        
        # 添加轮次信息
        prompt += f"\n\n这是会议的第1轮讨论，请分享您的初步想法。"
        
        # 记录会议开始
        self.discussion_history.append({
            "round": 1,
            "prompt": prompt,
            "responses": {}
        })
        
        # 返回会议开始提示
        return f"已启动{self._get_conference_name()}，第1轮讨论已开始。"
    
    async def next_round(self, user_id: str, session_id: str) -> bool:
        """
        进行下一轮讨论
        
        参数:
        - user_id: 用户ID
        - session_id: 会话ID
        
        返回:
        - 是否是最后一轮
        """
        self.current_round += 1
        
        # 检查是否达到最大轮次
        if self.current_round >= self.max_rounds:
            await self.conclude_conference(user_id, session_id)
            return True
        
        # 获取会议提示
        base_prompt = get_conference_prompt(self.conference_type)
        
        # 添加轮次信息
        if self.current_round == self.max_rounds - 1:
            prompt = base_prompt + f"\n\n这是会议的第{self.current_round + 1}轮讨论，也是最后一轮。请基于之前的讨论总结您的最终观点。"
        else:
            prompt = base_prompt + f"\n\n这是会议的第{self.current_round + 1}轮讨论，请基于之前的讨论深入思考。"
        
        # 记录新一轮讨论
        self.discussion_history.append({
            "round": self.current_round + 1,
            "prompt": prompt,
            "responses": {}
        })
        
        return False
    
    async def conclude_conference(self, user_id: str, session_id: str) -> str:
        """
        总结会议结果
        
        参数:
        - user_id: 用户ID
        - session_id: 会话ID
        
        返回:
        - 会议总结
        """
        self.is_completed = True
        
        # 获取会议结果模板
        result_template = get_conference_result_template(self.conference_type)
        
        # 构建会议总结提示
        summary_prompt = f"""
作为对冲基金经理Otto，请总结{self._get_conference_name()}的讨论结果。

会议进行了{self.current_round + 1}轮讨论。

请使用以下模板总结会议结果：

{result_template}
"""
        
        # 让主持人总结会议结果
        try:
            summary_response = await self.supervisor_agent.lead_agent.process_request(
                summary_prompt,
                user_id,
                session_id,
                []
            )
            
            # 记录会议总结
            if summary_response:
                if isinstance(summary_response.output, str):
                    summary = summary_response.output
                elif isinstance(summary_response.output, ConversationMessage):
                    summary = summary_response.output.content[0].get('text', '')
                else:
                    summary = "会议总结生成失败。"
                
                self.discussion_history.append({
                    "round": "summary",
                    "prompt": summary_prompt,
                    "responses": {"HedgeFundManager": summary}
                })
                
                return summary
            else:
                return "会议总结生成失败。"
        except Exception as e:
            print(f"生成会议总结时出错: {e}")
            return f"会议总结生成失败: {e}"
    
    def _get_conference_name(self) -> str:
        """获取会议名称"""
        if self.conference_type == "budget_allocation":
            return "预算分配会议"
        elif self.conference_type == "experience_sharing":
            return "经验分享会议"
        elif self.conference_type == "extreme_market":
            return "极端市场会议"
        else:
            return "未知会议"
