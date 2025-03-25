from typing import Dict, List, Any
import json
from datetime import datetime

class HedgeAgentMemorySystem:
    """
    HedgeAgents记忆系统，用于存储和检索三种类型的记忆：
    1. 市场信息记忆（Market Information）
    2. 投资反思记忆（Investment Reflection）
    3. 一般经验记忆（General Experience）
    """
    
    def __init__(self):
        """初始化记忆系统"""
        self.market_information = {}  # 市场信息记忆
        self.investment_reflection = {}  # 投资反思记忆
        self.general_experience = {}  # 一般经验记忆
    
    async def update_market_information(self, key: str, value: Any) -> Dict[str, Any]:
        """
        更新市场信息记忆
        
        参数:
        - key: 记忆键，如"BTC_trend"、"DJ30_support_levels"等
        - value: 记忆值，可以是任何类型
        
        返回:
        - 更新后的记忆条目
        """
        entry = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "type": "market_information"
        }
        self.market_information[key] = entry
        return entry
    
    async def update_investment_reflection(self, key: str, value: Any) -> Dict[str, Any]:
        """
        更新投资反思记忆
        
        参数:
        - key: 记忆键，如"BTC_buy_20250320"、"FX_strategy_review"等
        - value: 记忆值，可以是任何类型
        
        返回:
        - 更新后的记忆条目
        """
        entry = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "type": "investment_reflection"
        }
        self.investment_reflection[key] = entry
        return entry
    
    async def update_general_experience(self, key: str, value: Any) -> Dict[str, Any]:
        """
        更新一般经验记忆
        
        参数:
        - key: 记忆键，如"market_crash_response"、"volatility_strategy"等
        - value: 记忆值，可以是任何类型
        
        返回:
        - 更新后的记忆条目
        """
        entry = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "type": "general_experience"
        }
        self.general_experience[key] = entry
        return entry
    
    async def retrieve_memories(self, query: str = None) -> str:
        """
        检索记忆
        
        参数:
        - query: 可选的查询字符串，用于过滤记忆
        
        返回:
        - 包含三种记忆类型的格式化字符串
        """
        result_dict = {
            "market_information": {},
            "investment_reflection": {},
            "general_experience": {}
        }
        
        # 如果没有查询，返回所有记忆
        if not query:
            result_dict["market_information"] = self.market_information
            result_dict["investment_reflection"] = self.investment_reflection
            result_dict["general_experience"] = self.general_experience
        else:
            # 如果有查询，过滤记忆
            query = query.lower()
            
            # 过滤市场信息记忆
            for key, entry in self.market_information.items():
                if query in key.lower() or (isinstance(entry["value"], str) and query in entry["value"].lower()):
                    result_dict["market_information"][key] = entry
            
            # 过滤投资反思记忆
            for key, entry in self.investment_reflection.items():
                if query in key.lower() or (isinstance(entry["value"], str) and query in entry["value"].lower()):
                    result_dict["investment_reflection"][key] = entry
            
            # 过滤一般经验记忆
            for key, entry in self.general_experience.items():
                if query in key.lower() or (isinstance(entry["value"], str) and query in entry["value"].lower()):
                    result_dict["general_experience"][key] = entry
        
        # 将字典转换为格式化的字符串
        result_str = f"""
记忆检索结果 {f'(查询: {query})' if query else '(所有记忆)'}
时间戳: {datetime.now().isoformat()}

1. 市场信息记忆 ({len(result_dict["market_information"])}项):
"""
        
        # 添加市场信息记忆
        if result_dict["market_information"]:
            for key, entry in result_dict["market_information"].items():
                result_str += f"   - {key}: {entry['value']} (记录时间: {entry['timestamp']})\n"
        else:
            result_str += "   无相关记忆\n"
        
        # 添加投资反思记忆
        result_str += f"\n2. 投资反思记忆 ({len(result_dict['investment_reflection'])}项):\n"
        if result_dict["investment_reflection"]:
            for key, entry in result_dict["investment_reflection"].items():
                result_str += f"   - {key}: {entry['value']} (记录时间: {entry['timestamp']})\n"
        else:
            result_str += "   无相关记忆\n"
        
        # 添加一般经验记忆
        result_str += f"\n3. 一般经验记忆 ({len(result_dict['general_experience'])}项):\n"
        if result_dict["general_experience"]:
            for key, entry in result_dict["general_experience"].items():
                result_str += f"   - {key}: {entry['value']} (记录时间: {entry['timestamp']})\n"
        else:
            result_str += "   无相关记忆\n"
        
        return result_str
    
    async def get_market_information(self, key: str = None) -> Dict[str, Any]:
        """
        获取市场信息记忆
        
        参数:
        - key: 可选的记忆键，如果不提供则返回所有市场信息记忆
        
        返回:
        - 市场信息记忆
        """
        if key:
            return {key: self.market_information.get(key)}
        return self.market_information
    
    async def get_investment_reflection(self, key: str = None) -> Dict[str, Any]:
        """
        获取投资反思记忆
        
        参数:
        - key: 可选的记忆键，如果不提供则返回所有投资反思记忆
        
        返回:
        - 投资反思记忆
        """
        if key:
            return {key: self.investment_reflection.get(key)}
        return self.investment_reflection
    
    async def get_general_experience(self, key: str = None) -> Dict[str, Any]:
        """
        获取一般经验记忆
        
        参数:
        - key: 可选的记忆键，如果不提供则返回所有一般经验记忆
        
        返回:
        - 一般经验记忆
        """
        if key:
            return {key: self.general_experience.get(key)}
        return self.general_experience
    
    async def delete_memory(self, memory_type: str, key: str) -> bool:
        """
        删除指定类型的记忆
        
        参数:
        - memory_type: 记忆类型，可以是"market_information"、"investment_reflection"或"general_experience"
        - key: 记忆键
        
        返回:
        - 是否成功删除
        """
        if memory_type == "market_information" and key in self.market_information:
            del self.market_information[key]
            return True
        elif memory_type == "investment_reflection" and key in self.investment_reflection:
            del self.investment_reflection[key]
            return True
        elif memory_type == "general_experience" and key in self.general_experience:
            del self.general_experience[key]
            return True
        return False
    
    async def clear_memories(self, memory_type: str = None) -> bool:
        """
        清除指定类型的所有记忆，如果不指定类型则清除所有记忆
        
        参数:
        - memory_type: 可选的记忆类型，可以是"market_information"、"investment_reflection"或"general_experience"
        
        返回:
        - 是否成功清除
        """
        if memory_type == "market_information":
            self.market_information = {}
        elif memory_type == "investment_reflection":
            self.investment_reflection = {}
        elif memory_type == "general_experience":
            self.general_experience = {}
        else:
            self.market_information = {}
            self.investment_reflection = {}
            self.general_experience = {}
        return True
    
    async def get_memory_stats(self) -> Dict[str, int]:
        """
        获取记忆统计信息
        
        返回:
        - 包含各类记忆数量的字典
        """
        return {
            "market_information_count": len(self.market_information),
            "investment_reflection_count": len(self.investment_reflection),
            "general_experience_count": len(self.general_experience),
            "total_memories": len(self.market_information) + len(self.investment_reflection) + len(self.general_experience)
        }
    
    async def export_memories(self) -> Dict[str, Any]:
        """
        导出所有记忆
        
        返回:
        - 包含所有记忆的字典
        """
        return {
            "market_information": self.market_information,
            "investment_reflection": self.investment_reflection,
            "general_experience": self.general_experience,
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
            if "market_information" in memories:
                self.market_information.update(memories["market_information"])
            if "investment_reflection" in memories:
                self.investment_reflection.update(memories["investment_reflection"])
            if "general_experience" in memories:
                self.general_experience.update(memories["general_experience"])
            return True
        except Exception as e:
            print(f"导入记忆失败: {e}")
            return False

# 预定义的一些记忆
default_market_information = {
    "BTC_trend": {
        "value": "上升趋势，近期突破关键阻力位",
        "timestamp": "2025-03-24T10:00:00",
        "type": "market_information"
    },
    "DJ30_support": {
        "value": "主要支撑位在38000点附近",
        "timestamp": "2025-03-24T10:05:00",
        "type": "market_information"
    },
    "EUR_USD_outlook": {
        "value": "短期看跌，受美联储政策影响",
        "timestamp": "2025-03-24T10:10:00",
        "type": "market_information"
    }
}

default_investment_reflection = {
    "BTC_buy_20250315": {
        "value": "在62000美元买入比特币是正确决策，市场随后上涨",
        "timestamp": "2025-03-20T15:00:00",
        "type": "investment_reflection"
    },
    "AAPL_sell_20250310": {
        "value": "过早卖出苹果股票，错过了后续上涨",
        "timestamp": "2025-03-15T14:30:00",
        "type": "investment_reflection"
    },
    "FX_hedge_20250305": {
        "value": "使用外汇对冲策略有效降低了投资组合波动性",
        "timestamp": "2025-03-10T11:20:00",
        "type": "investment_reflection"
    }
}

default_general_experience = {
    "market_crash_response": {
        "value": "市场崩盘时，保持冷静并分批买入优质资产通常是最佳策略",
        "timestamp": "2025-01-15T09:00:00",
        "type": "general_experience"
    },
    "diversification_principle": {
        "value": "资产多样化是降低风险的关键，但过度分散可能降低收益",
        "timestamp": "2025-02-10T16:45:00",
        "type": "general_experience"
    },
    "technical_vs_fundamental": {
        "value": "短期交易依赖技术分析，长期投资更应关注基本面",
        "timestamp": "2025-02-25T13:30:00",
        "type": "general_experience"
    }
}

# 初始化记忆系统的辅助函数
async def initialize_memory_system() -> HedgeAgentMemorySystem:
    """
    初始化记忆系统并加载预定义记忆
    
    返回:
    - 初始化后的记忆系统
    """
    memory_system = HedgeAgentMemorySystem()
    
    # 加载预定义的市场信息记忆
    for key, entry in default_market_information.items():
        await memory_system.update_market_information(key, entry["value"])
    
    # 加载预定义的投资反思记忆
    for key, entry in default_investment_reflection.items():
        await memory_system.update_investment_reflection(key, entry["value"])
    
    # 加载预定义的一般经验记忆
    for key, entry in default_general_experience.items():
        await memory_system.update_general_experience(key, entry["value"])
    
    return memory_system
