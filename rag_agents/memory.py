"""
RAG Agents记忆系统

实现记忆系统，用于存储：
1. 用户查询历史
2. 检索结果
3. 验证结果
"""

from typing import Dict, List, Any
import json
from datetime import datetime

class RAGMemorySystem:
    """
    RAG Agents记忆系统，用于存储和检索三种类型的记忆：
    1. 用户查询历史（Query History）
    2. 检索结果（Retrieval Results）
    3. 验证结果（Verification Results）
    """
    
    def __init__(self):
        """初始化记忆系统"""
        self.query_history = {}  # 用户查询历史
        self.retrieval_results = {}  # 检索结果
        self.verification_results = {}  # 验证结果
    
    async def update_query_history(self, query_id: str, query: str, is_valid: bool = None) -> Dict[str, Any]:
        """
        更新用户查询历史
        
        参数:
        - query_id: 查询ID
        - query: 用户查询内容
        - is_valid: 查询是否有效
        
        返回:
        - 更新后的记忆条目
        """
        entry = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "is_valid": is_valid,
            "type": "query_history"
        }
        self.query_history[query_id] = entry
        return entry
    
    async def update_retrieval_results(self, query_id: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        更新检索结果
        
        参数:
        - query_id: 查询ID
        - results: 检索结果列表
        
        返回:
        - 更新后的记忆条目
        """
        entry = {
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "type": "retrieval_results"
        }
        self.retrieval_results[query_id] = entry
        return entry
    
    async def update_verification_results(self, query_id: str, is_valid: bool, feedback: str = None) -> Dict[str, Any]:
        """
        更新验证结果
        
        参数:
        - query_id: 查询ID
        - is_valid: 查询是否有效
        - feedback: 验证反馈
        
        返回:
        - 更新后的记忆条目
        """
        entry = {
            "is_valid": is_valid,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat(),
            "type": "verification_results"
        }
        self.verification_results[query_id] = entry
        
        # 同时更新查询历史中的有效性
        if query_id in self.query_history:
            self.query_history[query_id]["is_valid"] = is_valid
        
        return entry
    
    async def get_query_history(self, query_id: str = None) -> Dict[str, Any]:
        """
        获取用户查询历史
        
        参数:
        - query_id: 可选的查询ID，如果不提供则返回所有查询历史
        
        返回:
        - 用户查询历史
        """
        if query_id:
            return {query_id: self.query_history.get(query_id)}
        return self.query_history
    
    async def get_retrieval_results(self, query_id: str = None) -> Dict[str, Any]:
        """
        获取检索结果
        
        参数:
        - query_id: 可选的查询ID，如果不提供则返回所有检索结果
        
        返回:
        - 检索结果
        """
        if query_id:
            return {query_id: self.retrieval_results.get(query_id)}
        return self.retrieval_results
    
    async def get_verification_results(self, query_id: str = None) -> Dict[str, Any]:
        """
        获取验证结果
        
        参数:
        - query_id: 可选的查询ID，如果不提供则返回所有验证结果
        
        返回:
        - 验证结果
        """
        if query_id:
            return {query_id: self.verification_results.get(query_id)}
        return self.verification_results
    
    async def get_query_context(self, query_id: str) -> Dict[str, Any]:
        """
        获取查询的完整上下文，包括查询历史、检索结果和验证结果
        
        参数:
        - query_id: 查询ID
        
        返回:
        - 查询上下文
        """
        context = {
            "query_history": self.query_history.get(query_id),
            "retrieval_results": self.retrieval_results.get(query_id),
            "verification_results": self.verification_results.get(query_id)
        }
        return context
    
    async def get_memory_stats(self) -> Dict[str, int]:
        """
        获取记忆统计信息
        
        返回:
        - 包含各类记忆数量的字典
        """
        return {
            "query_history_count": len(self.query_history),
            "retrieval_results_count": len(self.retrieval_results),
            "verification_results_count": len(self.verification_results),
            "total_memories": len(self.query_history) + len(self.retrieval_results) + len(self.verification_results)
        }
    
    async def export_memories(self) -> Dict[str, Any]:
        """
        导出所有记忆
        
        返回:
        - 包含所有记忆的字典
        """
        return {
            "query_history": self.query_history,
            "retrieval_results": self.retrieval_results,
            "verification_results": self.verification_results,
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
            if "query_history" in memories:
                self.query_history.update(memories["query_history"])
            if "retrieval_results" in memories:
                self.retrieval_results.update(memories["retrieval_results"])
            if "verification_results" in memories:
                self.verification_results.update(memories["verification_results"])
            return True
        except Exception as e:
            print(f"导入记忆失败: {e}")
            return False

# 初始化记忆系统的辅助函数
async def initialize_memory_system() -> RAGMemorySystem:
    """
    初始化记忆系统
    
    返回:
    - 初始化后的记忆系统
    """
    memory_system = RAGMemorySystem()
    return memory_system
