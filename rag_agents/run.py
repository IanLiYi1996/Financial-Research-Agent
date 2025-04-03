#!/usr/bin/env python
"""
RAG Agents启动脚本

用于启动RAG Agents多智能体系统
"""

import asyncio
import sys
import os
import dotenv

# 加载环境变量
dotenv.load_dotenv()

# 将当前目录添加到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入主程序
from rag_agents.main import main

if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main())
