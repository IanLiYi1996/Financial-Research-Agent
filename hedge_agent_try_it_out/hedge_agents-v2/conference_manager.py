"""
HedgeAgents-v2会议管理系统

实现多轮会议的管理和流程控制
"""

from typing import Dict, List, Any, Optional, Tuple
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
    
    def __init__(self, conference_type: str, supervisor_agent: SupervisorAgent, team_agents: List[BedrockLLMAgent], 
                 max_rounds: int = 3, auto_mode: bool = False, orchestrator: Optional[MultiAgentOrchestrator] = None):
        """
        初始化会议管理器
        
        参数:
        - conference_type: 会议类型，可以是"budget_allocation"、"experience_sharing"或"extreme_market"
        - supervisor_agent: 主持人智能体（对冲基金经理）
        - team_agents: 团队成员智能体列表（分析师）
        - max_rounds: 最大会议轮次
        - auto_mode: 是否启用自动模式（由Supervisor自动控制会议流程）
        - orchestrator: MultiAgentOrchestrator实例，用于自动模式下的请求处理
        """
        self.conference_type = conference_type
        self.supervisor_agent = supervisor_agent
        self.team_agents = team_agents
        self.max_rounds = max_rounds
        self.current_round = 0
        self.discussion_history = []
        self.is_completed = False
        self.conference_id = f"{conference_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.auto_mode = auto_mode
        self.orchestrator = orchestrator
        self.user_id = None
        self.session_id = None
        
    async def start_conference(self, user_id: str, session_id: str) -> str:
        """
        启动会议
        
        参数:
        - user_id: 用户ID
        - session_id: 会话ID
        
        返回:
        - 会议初始提示
        """
        # 存储用户ID和会话ID，用于自动模式
        self.user_id = user_id
        self.session_id = session_id
        
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
        
        # 如果是自动模式，启动自动会议流程
        if self.auto_mode and self.orchestrator:
            # 创建一个任务来异步运行自动会议流程
            asyncio.create_task(self._auto_conference_flow())
        
        # 返回会议开始提示
        return f"已启动{self._get_conference_name()}，第1轮讨论已开始。" + (
            " (自动模式：会议将由Supervisor自动管理，无需手动控制)" if self.auto_mode else ""
        )
    
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
        
        # 添加前一轮的讨论摘要（如果有）
        if len(self.discussion_history) > 0 and "responses" in self.discussion_history[-1]:
            prompt += "\n\n## 前一轮讨论摘要\n"
            for agent_name, response in self.discussion_history[-1]["responses"].items():
                if isinstance(response, str):
                    prompt += f"\n### {agent_name}的观点\n{response[:300]}...\n"
                elif hasattr(response, 'content') and response.content:
                    content = response.content[0].get('text', '') if isinstance(response.content, list) else ''
                    prompt += f"\n### {agent_name}的观点\n{content[:300]}...\n"
        
        # 记录新一轮讨论
        self.discussion_history.append({
            "round": self.current_round + 1,
            "prompt": prompt,
            "responses": {}
        })
        
        # 如果是自动模式，处理新一轮讨论
        if self.auto_mode and self.orchestrator:
            # 发送会议提示给主导智能体
            classifier_result = ClassifierResult(selected_agent=self.supervisor_agent, confidence=1.0)
            await self.orchestrator.agent_process_request(prompt, user_id, session_id, classifier_result)
        
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
    
    async def evaluate_discussion(self, user_id: str, session_id: str) -> Tuple[bool, str]:
        """
        评估当前轮次的讨论质量和完整性
        
        参数:
        - user_id: 用户ID
        - session_id: 会话ID
        
        返回:
        - (是否继续讨论, 评估结果)
        """
        # 构建评估提示
        evaluation_prompt = f"""
作为对冲基金经理Otto，请评估当前第{self.current_round + 1}轮{self._get_conference_name()}讨论的质量和完整性。

评估标准:
1. 讨论深度: 分析师是否深入探讨了相关话题
2. 覆盖面: 是否涵盖了所有重要方面
3. 意见一致性: 分析师之间的意见是否存在重大分歧
4. 信息充分性: 是否有足够的信息做出决策

请根据以上标准评估，并决定:
1. 是否需要继续讨论（进入下一轮）
2. 是否可以结束讨论并总结会议结果

请以JSON格式回答:
{{
  "continue_discussion": true/false,
  "reason": "解释为什么继续或结束讨论",
  "evaluation": "对当前讨论的简要评估"
}}
"""
        
        try:
            # 让主持人评估讨论
            evaluation_response = await self.supervisor_agent.lead_agent.process_request(
                evaluation_prompt,
                user_id,
                session_id,
                []
            )
            
            # 解析评估结果
            if evaluation_response:
                if isinstance(evaluation_response.output, str):
                    evaluation_text = evaluation_response.output
                elif isinstance(evaluation_response.output, ConversationMessage):
                    evaluation_text = evaluation_response.output.content[0].get('text', '')
                else:
                    evaluation_text = "{}"
                
                # 尝试解析JSON
                import json
                import re
                
                # 提取JSON部分（可能嵌入在其他文本中）
                json_match = re.search(r'\{.*\}', evaluation_text, re.DOTALL)
                if json_match:
                    evaluation_json = json_match.group(0)
                    try:
                        evaluation = json.loads(evaluation_json)
                        continue_discussion = evaluation.get("continue_discussion", True)
                        reason = evaluation.get("reason", "未提供原因")
                        evaluation_summary = evaluation.get("evaluation", "未提供评估")
                        
                        return (continue_discussion, f"评估结果: {evaluation_summary}\n原因: {reason}")
                    except json.JSONDecodeError:
                        # 如果JSON解析失败，默认继续讨论
                        return (True, "无法解析评估结果，默认继续讨论。")
                else:
                    # 如果找不到JSON，默认继续讨论
                    return (True, "无法找到评估结果，默认继续讨论。")
            else:
                return (True, "评估失败，默认继续讨论。")
        except Exception as e:
            print(f"评估讨论时出错: {e}")
            return (True, f"评估出错: {e}，默认继续讨论。")
    
    async def _auto_conference_flow(self):
        """
        自动会议流程控制
        """
        if not self.auto_mode or not self.orchestrator or not self.user_id or not self.session_id:
            return
        
        try:
            # 等待一段时间，让第一轮讨论完成
            await asyncio.sleep(5)
            
            # 循环处理会议流程
            while not self.is_completed and self.current_round < self.max_rounds:
                # 评估当前讨论
                continue_discussion, evaluation = await self.evaluate_discussion(self.user_id, self.session_id)
                
                # 打印评估结果
                print(f"\n\033[33m[Supervisor评估] {evaluation}\033[0m")
                
                if continue_discussion and self.current_round < self.max_rounds - 1:
                    # 继续下一轮讨论
                    print(f"\n\033[33m[Supervisor决定] 继续进行下一轮讨论\033[0m")
                    is_final = await self.next_round(self.user_id, self.session_id)
                    
                    # 等待一段时间，让讨论完成
                    await asyncio.sleep(5)
                else:
                    # 结束会议
                    print(f"\n\033[33m[Supervisor决定] 讨论已充分，结束会议\033[0m")
                    summary = await self.conclude_conference(self.user_id, self.session_id)
                    print(f"\n\033[34m{summary}\033[0m")
                    break
        except Exception as e:
            print(f"\n自动会议流程出错: {e}")
            import traceback
            traceback.print_exc()
    
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
