"""
RAG Agents - 基于multi-agent-orchestrator的多智能体RAG系统

这个包实现了一个多智能体RAG系统，包括：
1. 输入检查智能体（InputVerifierAgent）
2. RAG智能体（RAGAgent）
3. 主导智能体（SupervisorAgent）
4. 记忆系统
5. 知识库检索工具
"""

from .main import rag_supervisor
from .tools import knowledge_base_search
from .memory import RAGMemorySystem, initialize_memory_system

__version__ = "0.1.0"
