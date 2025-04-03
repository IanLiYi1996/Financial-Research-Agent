from typing import Dict, List, Any
import json
from datetime import datetime

class FundAdvisorMemorySystem:
    """
    基金投顾记忆系统，用于存储和检索三种类型的记忆：
    1. 用户画像记忆（User Profile）
    2. 基金知识记忆（Fund Knowledge）
    3. 交互历史记忆（Interaction History）
    """
    
    def __init__(self):
        """初始化记忆系统"""
        self.user_profile = {}  # 用户画像记忆
        self.fund_knowledge = {}  # 基金知识记忆
        self.interaction_history = {}  # 交互历史记忆
    
    async def update_user_profile(self, user_id: str, profile_data: Any) -> Dict[str, Any]:
        """
        更新用户画像记忆
        
        参数:
        - user_id: 用户ID
        - profile_data: 用户画像数据，可以是任何类型
        
        返回:
        - 更新后的记忆条目
        """
        entry = {
            "value": profile_data,
            "timestamp": datetime.now().isoformat(),
            "type": "user_profile"
        }
        
        if user_id not in self.user_profile:
            self.user_profile[user_id] = {}
            
        # 如果profile_data是字典，则更新用户画像的特定字段
        if isinstance(profile_data, dict):
            for key, value in profile_data.items():
                self.user_profile[user_id][key] = {
                    "value": value,
                    "timestamp": datetime.now().isoformat(),
                    "type": "user_profile"
                }
            return self.user_profile[user_id]
        else:
            # 如果不是字典，则将整个数据作为一个条目存储
            key = f"profile_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.user_profile[user_id][key] = entry
            return {key: entry}
    
    async def update_fund_knowledge(self, key: str, value: Any) -> Dict[str, Any]:
        """
        更新基金知识记忆
        
        参数:
        - key: 记忆键，如"fund_type_description"、"risk_level_explanation"等
        - value: 记忆值，可以是任何类型
        
        返回:
        - 更新后的记忆条目
        """
        entry = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "type": "fund_knowledge"
        }
        self.fund_knowledge[key] = entry
        return entry
    
    async def update_interaction_history(self, user_id: str, interaction_data: Any) -> Dict[str, Any]:
        """
        更新交互历史记忆
        
        参数:
        - user_id: 用户ID
        - interaction_data: 交互数据，可以是任何类型
        
        返回:
        - 更新后的记忆条目
        """
        entry = {
            "value": interaction_data,
            "timestamp": datetime.now().isoformat(),
            "type": "interaction_history"
        }
        
        if user_id not in self.interaction_history:
            self.interaction_history[user_id] = []
            
        self.interaction_history[user_id].append(entry)
        return entry
    
    async def retrieve_memories(self, query: str = None, user_id: str = None) -> str:
        """
        检索记忆
        
        参数:
        - query: 可选的查询字符串，用于过滤记忆
        - user_id: 可选的用户ID，用于限制检索范围
        
        返回:
        - 包含三种记忆类型的格式化字符串
        """
        result_dict = {
            "user_profile": {},
            "fund_knowledge": {},
            "interaction_history": {}
        }
        
        # 过滤用户画像记忆
        if user_id:
            # 如果指定了用户ID，只检索该用户的画像
            if user_id in self.user_profile:
                if query:
                    # 如果有查询，过滤记忆
                    query = query.lower()
                    for key, entry in self.user_profile[user_id].items():
                        if query in key.lower() or (isinstance(entry["value"], str) and query in entry["value"].lower()):
                            result_dict["user_profile"][key] = entry
                else:
                    # 如果没有查询，返回该用户的所有画像
                    result_dict["user_profile"] = self.user_profile[user_id]
        else:
            # 如果没有指定用户ID，检索所有用户的画像
            if query:
                # 如果有查询，过滤记忆
                query = query.lower()
                for user_id, user_data in self.user_profile.items():
                    for key, entry in user_data.items():
                        if query in key.lower() or (isinstance(entry["value"], str) and query in entry["value"].lower()):
                            if user_id not in result_dict["user_profile"]:
                                result_dict["user_profile"][user_id] = {}
                            result_dict["user_profile"][user_id][key] = entry
            else:
                # 如果没有查询，返回所有用户的画像
                result_dict["user_profile"] = self.user_profile
        
        # 过滤基金知识记忆
        if query:
            # 如果有查询，过滤记忆
            query = query.lower()
            for key, entry in self.fund_knowledge.items():
                if query in key.lower() or (isinstance(entry["value"], str) and query in entry["value"].lower()):
                    result_dict["fund_knowledge"][key] = entry
        else:
            # 如果没有查询，返回所有基金知识
            result_dict["fund_knowledge"] = self.fund_knowledge
        
        # 过滤交互历史记忆
        if user_id:
            # 如果指定了用户ID，只检索该用户的交互历史
            if user_id in self.interaction_history:
                if query:
                    # 如果有查询，过滤记忆
                    query = query.lower()
                    result_dict["interaction_history"][user_id] = []
                    for entry in self.interaction_history[user_id]:
                        if isinstance(entry["value"], str) and query in entry["value"].lower():
                            result_dict["interaction_history"][user_id].append(entry)
                else:
                    # 如果没有查询，返回该用户的所有交互历史
                    result_dict["interaction_history"][user_id] = self.interaction_history[user_id]
        else:
            # 如果没有指定用户ID，检索所有用户的交互历史
            if query:
                # 如果有查询，过滤记忆
                query = query.lower()
                for user_id, interactions in self.interaction_history.items():
                    for entry in interactions:
                        if isinstance(entry["value"], str) and query in entry["value"].lower():
                            if user_id not in result_dict["interaction_history"]:
                                result_dict["interaction_history"][user_id] = []
                            result_dict["interaction_history"][user_id].append(entry)
            else:
                # 如果没有查询，返回所有用户的交互历史
                result_dict["interaction_history"] = self.interaction_history
        
        # 将字典转换为格式化的字符串
        result_str = f"""
记忆检索结果 {f'(查询: {query})' if query else ''} {f'(用户ID: {user_id})' if user_id else ''}
时间戳: {datetime.now().isoformat()}

1. 用户画像记忆:
"""
        
        # 添加用户画像记忆
        if isinstance(result_dict["user_profile"], dict) and result_dict["user_profile"]:
            if user_id and user_id in result_dict["user_profile"]:
                # 单个用户的画像
                for key, entry in result_dict["user_profile"].items():
                    result_str += f"   - {key}: {entry['value']} (记录时间: {entry['timestamp']})\n"
            else:
                # 多个用户的画像
                for uid, user_data in result_dict["user_profile"].items():
                    result_str += f"   用户 {uid}:\n"
                    for key, entry in user_data.items():
                        result_str += f"     - {key}: {entry['value']} (记录时间: {entry['timestamp']})\n"
        else:
            result_str += "   无相关记忆\n"
        
        # 添加基金知识记忆
        result_str += f"\n2. 基金知识记忆:\n"
        if result_dict["fund_knowledge"]:
            for key, entry in result_dict["fund_knowledge"].items():
                result_str += f"   - {key}: {entry['value']} (记录时间: {entry['timestamp']})\n"
        else:
            result_str += "   无相关记忆\n"
        
        # 添加交互历史记忆
        result_str += f"\n3. 交互历史记忆:\n"
        if result_dict["interaction_history"]:
            if user_id and user_id in result_dict["interaction_history"]:
                # 单个用户的交互历史
                for entry in result_dict["interaction_history"]:
                    result_str += f"   - {entry['timestamp']}: {entry['value']}\n"
            else:
                # 多个用户的交互历史
                for uid, interactions in result_dict["interaction_history"].items():
                    result_str += f"   用户 {uid}:\n"
                    for entry in interactions:
                        result_str += f"     - {entry['timestamp']}: {entry['value']}\n"
        else:
            result_str += "   无相关记忆\n"
        
        return result_str
    
    async def get_user_profile(self, user_id: str = None, key: str = None) -> Dict[str, Any]:
        """
        获取用户画像记忆
        
        参数:
        - user_id: 可选的用户ID，如果不提供则返回所有用户的画像
        - key: 可选的记忆键，如果不提供则返回指定用户的所有画像
        
        返回:
        - 用户画像记忆
        """
        if user_id:
            if user_id in self.user_profile:
                if key:
                    return {key: self.user_profile[user_id].get(key)}
                return self.user_profile[user_id]
            return {}
        return self.user_profile
    
    async def get_fund_knowledge(self, key: str = None) -> Dict[str, Any]:
        """
        获取基金知识记忆
        
        参数:
        - key: 可选的记忆键，如果不提供则返回所有基金知识记忆
        
        返回:
        - 基金知识记忆
        """
        if key:
            return {key: self.fund_knowledge.get(key)}
        return self.fund_knowledge
    
    async def get_interaction_history(self, user_id: str = None) -> Dict[str, Any]:
        """
        获取交互历史记忆
        
        参数:
        - user_id: 可选的用户ID，如果不提供则返回所有用户的交互历史
        
        返回:
        - 交互历史记忆
        """
        if user_id:
            if user_id in self.interaction_history:
                return {user_id: self.interaction_history[user_id]}
            return {}
        return self.interaction_history
    
    async def delete_memory(self, memory_type: str, key: str, user_id: str = None) -> bool:
        """
        删除指定类型的记忆
        
        参数:
        - memory_type: 记忆类型，可以是"user_profile"、"fund_knowledge"或"interaction_history"
        - key: 记忆键
        - user_id: 可选的用户ID，用于删除特定用户的记忆
        
        返回:
        - 是否成功删除
        """
        if memory_type == "user_profile" and user_id and user_id in self.user_profile and key in self.user_profile[user_id]:
            del self.user_profile[user_id][key]
            return True
        elif memory_type == "fund_knowledge" and key in self.fund_knowledge:
            del self.fund_knowledge[key]
            return True
        elif memory_type == "interaction_history" and user_id and user_id in self.interaction_history:
            # 对于交互历史，key是索引
            try:
                index = int(key)
                if 0 <= index < len(self.interaction_history[user_id]):
                    del self.interaction_history[user_id][index]
                    return True
            except ValueError:
                pass
        return False
    
    async def clear_memories(self, memory_type: str = None, user_id: str = None) -> bool:
        """
        清除指定类型的所有记忆，如果不指定类型则清除所有记忆
        
        参数:
        - memory_type: 可选的记忆类型，可以是"user_profile"、"fund_knowledge"或"interaction_history"
        - user_id: 可选的用户ID，用于清除特定用户的记忆
        
        返回:
        - 是否成功清除
        """
        if memory_type == "user_profile":
            if user_id:
                if user_id in self.user_profile:
                    self.user_profile[user_id] = {}
            else:
                self.user_profile = {}
        elif memory_type == "fund_knowledge":
            self.fund_knowledge = {}
        elif memory_type == "interaction_history":
            if user_id:
                if user_id in self.interaction_history:
                    self.interaction_history[user_id] = []
            else:
                self.interaction_history = {}
        else:
            if user_id:
                if user_id in self.user_profile:
                    self.user_profile[user_id] = {}
                if user_id in self.interaction_history:
                    self.interaction_history[user_id] = []
            else:
                self.user_profile = {}
                self.fund_knowledge = {}
                self.interaction_history = {}
        return True
    
    async def get_memory_stats(self) -> Dict[str, int]:
        """
        获取记忆统计信息
        
        返回:
        - 包含各类记忆数量的字典
        """
        user_profile_count = sum(len(user_data) for user_data in self.user_profile.values())
        fund_knowledge_count = len(self.fund_knowledge)
        interaction_history_count = sum(len(interactions) for interactions in self.interaction_history.values())
        
        return {
            "user_profile_count": user_profile_count,
            "fund_knowledge_count": fund_knowledge_count,
            "interaction_history_count": interaction_history_count,
            "total_memories": user_profile_count + fund_knowledge_count + interaction_history_count
        }
    
    async def export_memories(self) -> Dict[str, Any]:
        """
        导出所有记忆
        
        返回:
        - 包含所有记忆的字典
        """
        return {
            "user_profile": self.user_profile,
            "fund_knowledge": self.fund_knowledge,
            "interaction_history": self.interaction_history,
            "export_timestamp": datetime.now().isoformat()
        }
    
    async def import_memories(self, memories: Dict[str, Any]) -> bool:
        """
        导入记忆
        
        参数:
        - memories: 包含记忆的字典，格式应与export_memories方法的返回值相同
        
        返回:
        - 是否成功导入
        """
        try:
            if "user_profile" in memories:
                self.user_profile.update(memories["user_profile"])
            if "fund_knowledge" in memories:
                self.fund_knowledge.update(memories["fund_knowledge"])
            if "interaction_history" in memories:
                for user_id, interactions in memories["interaction_history"].items():
                    if user_id not in self.interaction_history:
                        self.interaction_history[user_id] = []
                    self.interaction_history[user_id].extend(interactions)
            return True
        except Exception as e:
            print(f"导入记忆失败: {e}")
            return False

# 预定义的一些记忆
default_fund_knowledge = {
    "fund_types": {
        "value": {
            "股票型": "主要投资于股票市场，风险较高，收益潜力较大",
            "债券型": "主要投资于债券市场，风险较低，收益相对稳定",
            "混合型": "同时投资于股票和债券，风险和收益介于股票型和债券型之间",
            "指数型": "追踪特定指数，如沪深300指数，风险和收益取决于所跟踪的指数",
            "货币型": "投资于货币市场工具，风险最低，收益也相对较低"
        },
        "timestamp": "2025-04-01T10:00:00",
        "type": "fund_knowledge"
    },
    "risk_levels": {
        "value": {
            "保守型": "适合风险承受能力较低的投资者，追求本金安全和稳定收益",
            "稳健型": "适合风险承受能力中等偏低的投资者，追求相对稳定的收益",
            "平衡型": "适合风险承受能力中等的投资者，追求收益和风险的平衡",
            "成长型": "适合风险承受能力中等偏高的投资者，追求较高收益",
            "进取型": "适合风险承受能力较高的投资者，追求高收益，能够承受较大波动"
        },
        "timestamp": "2025-04-01T10:05:00",
        "type": "fund_knowledge"
    },
    "investment_principles": {
        "value": [
            "分散投资，降低风险",
            "长期投资，享受复利",
            "定期定额，平均成本",
            "根据风险承受能力选择合适的基金",
            "定期评估和调整投资组合"
        ],
        "timestamp": "2025-04-01T10:10:00",
        "type": "fund_knowledge"
    }
}

# 初始化记忆系统的辅助函数
async def initialize_memory_system() -> FundAdvisorMemorySystem:
    """
    初始化记忆系统并加载预定义记忆
    
    返回:
    - 初始化后的记忆系统
    """
    memory_system = FundAdvisorMemorySystem()
    
    # 加载预定义的基金知识记忆
    for key, entry in default_fund_knowledge.items():
        await memory_system.update_fund_knowledge(key, entry["value"])
    
    return memory_system
