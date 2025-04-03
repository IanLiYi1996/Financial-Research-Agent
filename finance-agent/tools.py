from typing import Dict, List, Any
import asyncio
import json
import random
from datetime import datetime
import boto3
import requests
from boto3.dynamodb.conditions import Key, Attr

# 工具描述

# Nebula知识图谱工具描述
nebula_description = [{
    "toolSpec": {
        "name": "query_nebula_knowledge_graph",
        "description": "查询Nebula知识图谱，获取基金相关信息",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "查询语句，使用nGQL语法"
                    }
                },
                "required": ["query"]
            }
        }
    }
}]

# OpenSearch金融知识工具描述
opensearch_description = [{
    "toolSpec": {
        "name": "query_opensearch_knowledge",
        "description": "查询OpenSearch金融知识库，获取金融和基金相关知识",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "查询关键词或短语"
                    },
                    "size": {
                        "type": "number",
                        "description": "返回结果数量，默认为5"
                    }
                },
                "required": ["query"]
            }
        }
    }
}]

# DynamoDB用户信息工具描述
dynamodb_description = [{
    "toolSpec": {
        "name": "query_dynamodb_user_info",
        "description": "查询DynamoDB中的用户基本信息",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "用户ID"
                    }
                },
                "required": ["user_id"]
            }
        }
    }
}, {
    "toolSpec": {
        "name": "update_dynamodb_user_info",
        "description": "更新DynamoDB中的用户基本信息",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "用户ID"
                    },
                    "user_info": {
                        "type": "object",
                        "description": "用户信息，包括姓名、年龄、收入、投资经验等"
                    },
                    "risk_profile": {
                        "type": "string",
                        "description": "用户风险偏好，可以是保守型、稳健型、平衡型、成长型、进取型"
                    }
                },
                "required": ["user_id", "user_info"]
            }
        }
    }
}]

# 搜索金融信息工具描述
search_description = [{
    "toolSpec": {
        "name": "search_financial_info",
        "description": "使用搜索引擎查询最新的金融信息",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或短语"
                    },
                    "num_results": {
                        "type": "number",
                        "description": "返回结果数量，默认为5"
                    }
                },
                "required": ["query"]
            }
        }
    }
}]

# 模拟数据

# 模拟基金数据
fund_data = {
    "000001": {
        "fund_name": "华夏成长混合",
        "fund_type": "混合型",
        "risk_level": "平衡型",
        "manager": "王阳",
        "establishment_date": "2001-12-18",
        "fund_size": 56.78,  # 单位：亿元
        "nav": 1.2345,  # 单位净值
        "annual_return": {
            "1y": 0.0823,  # 8.23%
            "3y": 0.2567,  # 25.67%
            "5y": 0.4321,  # 43.21%
        },
        "volatility": 0.15,  # 波动率
        "sharpe_ratio": 0.85,  # 夏普比率
        "max_drawdown": 0.25,  # 最大回撤
        "investment_strategy": "本基金主要投资于具有良好成长性的上市公司股票，通过精选个股和适度的资产配置，分享中国经济和资本市场高速成长的成果。",
        "top_holdings": [
            {"stock": "贵州茅台", "proportion": 0.0856},
            {"stock": "招商银行", "proportion": 0.0654},
            {"stock": "腾讯控股", "proportion": 0.0532},
            {"stock": "美的集团", "proportion": 0.0478},
            {"stock": "宁德时代", "proportion": 0.0423}
        ]
    },
    "000002": {
        "fund_name": "华夏债券A",
        "fund_type": "债券型",
        "risk_level": "稳健型",
        "manager": "李明",
        "establishment_date": "2002-10-23",
        "fund_size": 102.45,  # 单位：亿元
        "nav": 1.5678,  # 单位净值
        "annual_return": {
            "1y": 0.0456,  # 4.56%
            "3y": 0.1234,  # 12.34%
            "5y": 0.2345,  # 23.45%
        },
        "volatility": 0.05,  # 波动率
        "sharpe_ratio": 0.95,  # 夏普比率
        "max_drawdown": 0.08,  # 最大回撤
        "investment_strategy": "本基金主要投资于国债、金融债、企业债等固定收益类金融工具，在保证基金资产安全性和流动性的基础上，追求长期稳定的投资回报。",
        "top_holdings": [
            {"bond": "国债2101", "proportion": 0.0956},
            {"bond": "农发债2205", "proportion": 0.0854},
            {"bond": "工商银行CD", "proportion": 0.0732},
            {"bond": "中石油债", "proportion": 0.0678},
            {"bond": "铁道债", "proportion": 0.0623}
        ]
    },
    "000003": {
        "fund_name": "嘉实沪深300ETF",
        "fund_type": "指数型",
        "risk_level": "成长型",
        "manager": "张华",
        "establishment_date": "2005-04-08",
        "fund_size": 156.78,  # 单位：亿元
        "nav": 1.0234,  # 单位净值
        "annual_return": {
            "1y": 0.0912,  # 9.12%
            "3y": 0.2789,  # 27.89%
            "5y": 0.3456,  # 34.56%
        },
        "volatility": 0.18,  # 波动率
        "sharpe_ratio": 0.78,  # 夏普比率
        "max_drawdown": 0.30,  # 最大回撤
        "investment_strategy": "本基金采用完全复制法，通过指数化投资方式，跟踪沪深300指数，力求获得与标的指数相似的回报。",
        "top_holdings": [
            {"stock": "贵州茅台", "proportion": 0.0756},
            {"stock": "招商银行", "proportion": 0.0554},
            {"stock": "中国平安", "proportion": 0.0532},
            {"stock": "工商银行", "proportion": 0.0478},
            {"stock": "恒瑞医药", "proportion": 0.0423}
        ]
    },
    "000004": {
        "fund_name": "易方达消费精选",
        "fund_type": "股票型",
        "risk_level": "进取型",
        "manager": "刘强",
        "establishment_date": "2010-08-16",
        "fund_size": 78.45,  # 单位：亿元
        "nav": 2.3456,  # 单位净值
        "annual_return": {
            "1y": 0.1234,  # 12.34%
            "3y": 0.4567,  # 45.67%
            "5y": 0.7890,  # 78.90%
        },
        "volatility": 0.25,  # 波动率
        "sharpe_ratio": 0.92,  # 夏普比率
        "max_drawdown": 0.35,  # 最大回撤
        "investment_strategy": "本基金主要投资于消费行业的上市公司，通过精选个股，分享中国消费升级带来的投资机会。",
        "top_holdings": [
            {"stock": "贵州茅台", "proportion": 0.0956},
            {"stock": "五粮液", "proportion": 0.0854},
            {"stock": "海天味业", "proportion": 0.0732},
            {"stock": "伊利股份", "proportion": 0.0678},
            {"stock": "美的集团", "proportion": 0.0623}
        ]
    },
    "000005": {
        "fund_name": "南方货币A",
        "fund_type": "货币型",
        "risk_level": "保守型",
        "manager": "周静",
        "establishment_date": "2004-12-03",
        "fund_size": 345.67,  # 单位：亿元
        "nav": 1.0000,  # 单位净值
        "annual_return": {
            "1y": 0.0234,  # 2.34%
            "3y": 0.0789,  # 7.89%
            "5y": 0.1234,  # 12.34%
        },
        "volatility": 0.01,  # 波动率
        "sharpe_ratio": 0.65,  # 夏普比率
        "max_drawdown": 0.00,  # 最大回撤
        "investment_strategy": "本基金主要投资于货币市场工具，在保持本金安全和资产流动性的前提下，力求获得高于同期银行活期存款利率的投资收益。",
        "top_holdings": [
            {"instrument": "银行存款", "proportion": 0.2356},
            {"instrument": "国债逆回购", "proportion": 0.1854},
            {"instrument": "同业存单", "proportion": 0.1732},
            {"instrument": "商业票据", "proportion": 0.1278},
            {"instrument": "短期融资券", "proportion": 0.1123}
        ]
    }
}

# 模拟用户数据
user_data = {
    "user123": {
        "user_info": {
            "name": "张三",
            "age": 35,
            "gender": "男",
            "occupation": "工程师",
            "annual_income": 300000,  # 年收入
            "investment_experience": 5,  # 投资经验（年）
            "education": "本科",
            "financial_assets": 1000000,  # 金融资产（元）
            "investment_horizon": 10,  # 投资期限（年）
            "investment_goal": "子女教育和退休规划"
        },
        "risk_profile": "平衡型",
        "investment_preferences": {
            "preferred_fund_types": ["混合型", "指数型"],
            "avoid_industries": ["博彩", "烟草"],
            "esg_preference": True,  # 是否关注ESG投资
            "dividend_preference": False  # 是否偏好分红
        },
        "portfolio": [
            {"fund_id": "000001", "amount": 50000},
            {"fund_id": "000003", "amount": 30000},
            {"fund_id": "000005", "amount": 20000}
        ]
    },
    "user456": {
        "user_info": {
            "name": "李四",
            "age": 55,
            "gender": "男",
            "occupation": "教师",
            "annual_income": 200000,  # 年收入
            "investment_experience": 10,  # 投资经验（年）
            "education": "硕士",
            "financial_assets": 2000000,  # 金融资产（元）
            "investment_horizon": 5,  # 投资期限（年）
            "investment_goal": "退休规划"
        },
        "risk_profile": "稳健型",
        "investment_preferences": {
            "preferred_fund_types": ["债券型", "货币型"],
            "avoid_industries": ["互联网", "游戏"],
            "esg_preference": False,  # 是否关注ESG投资
            "dividend_preference": True  # 是否偏好分红
        },
        "portfolio": [
            {"fund_id": "000002", "amount": 100000},
            {"fund_id": "000005", "amount": 50000}
        ]
    },
    "user789": {
        "user_info": {
            "name": "王五",
            "age": 28,
            "gender": "女",
            "occupation": "医生",
            "annual_income": 400000,  # 年收入
            "investment_experience": 3,  # 投资经验（年）
            "education": "博士",
            "financial_assets": 800000,  # 金融资产（元）
            "investment_horizon": 20,  # 投资期限（年）
            "investment_goal": "财富增长"
        },
        "risk_profile": "进取型",
        "investment_preferences": {
            "preferred_fund_types": ["股票型", "指数型"],
            "avoid_industries": [],
            "esg_preference": True,  # 是否关注ESG投资
            "dividend_preference": False  # 是否偏好分红
        },
        "portfolio": [
            {"fund_id": "000003", "amount": 50000},
            {"fund_id": "000004", "amount": 100000}
        ]
    }
}

# 模拟金融知识库
financial_knowledge = [
    {
        "id": "k001",
        "title": "什么是基金？",
        "content": "基金是一种利益共享、风险共担的集合投资工具，由基金管理人管理，基金托管人托管，通过发行基金份额募集资金，将资金投资于股票、债券等金融工具的投资组合。基金投资人通过购买基金份额成为基金持有人，按持有份额分享投资收益，承担投资风险。",
        "keywords": ["基金", "基金定义", "集合投资", "基金份额"],
        "category": "基础知识"
    },
    {
        "id": "k002",
        "title": "基金的分类",
        "content": "基金可以按多种标准分类：1）按投资标的分为股票型基金、债券型基金、混合型基金、货币市场基金等；2）按运作方式分为开放式基金和封闭式基金；3）按投资目标分为成长型基金、收入型基金、平衡型基金等；4）按投资区域分为国内基金、国际基金、全球基金等。",
        "keywords": ["基金分类", "股票型基金", "债券型基金", "混合型基金", "货币市场基金", "开放式基金", "封闭式基金"],
        "category": "基础知识"
    },
    {
        "id": "k003",
        "title": "基金净值是什么？",
        "content": "基金净值是指基金单位份额的价值，等于基金资产总值减去基金负债后的余额，再除以基金总份额。基金净值是衡量基金表现的重要指标，投资者可以通过比较不同时期的基金净值来了解基金的收益情况。基金净值通常每个交易日公布一次。",
        "keywords": ["基金净值", "单位净值", "净值计算", "基金表现"],
        "category": "基础知识"
    },
    {
        "id": "k004",
        "title": "什么是基金的申购和赎回？",
        "content": "申购是指投资者购买基金份额的行为，赎回是指投资者卖出基金份额的行为。开放式基金允许投资者在基金存续期内任何交易日进行申购和赎回。申购价格为申购当日的基金净值，赎回价格为赎回当日的基金净值。申购和赎回通常会收取一定的费用。",
        "keywords": ["基金申购", "基金赎回", "开放式基金", "申购费", "赎回费"],
        "category": "基金交易"
    },
    {
        "id": "k005",
        "title": "基金投资的风险有哪些？",
        "content": "基金投资面临多种风险：1）市场风险：市场价格波动导致的投资损失；2）流动性风险：无法及时变现或变现成本过高；3）管理风险：基金管理人的管理能力和投资策略失误；4）信用风险：债券发行人违约风险；5）操作风险：内部流程、人员和系统的不完善；6）特定投资标的风险：如股票、债券、衍生品等特定风险。",
        "keywords": ["基金风险", "市场风险", "流动性风险", "管理风险", "信用风险", "操作风险"],
        "category": "风险管理"
    },
    {
        "id": "k006",
        "title": "如何选择适合自己的基金？",
        "content": "选择基金应考虑以下因素：1）个人风险承受能力和投资目标；2）基金的历史业绩和波动性；3）基金经理的投资能力和经验；4）基金的费用结构；5）基金公司的规模和声誉；6）基金的投资策略是否符合市场趋势。投资者应根据自身情况选择适合的基金类型，并定期评估基金表现。",
        "keywords": ["基金选择", "风险承受能力", "基金业绩", "基金经理", "费用结构", "投资策略"],
        "category": "投资策略"
    },
    {
        "id": "k007",
        "title": "什么是ETF？",
        "content": "ETF（Exchange Traded Fund）是交易型开放式指数基金，结合了开放式基金和封闭式基金的优点。ETF在证券交易所上市交易，投资者可以像买卖股票一样买卖ETF份额。ETF通常跟踪特定指数，如沪深300指数、标普500指数等，具有透明度高、交易便捷、费用低廉等特点。",
        "keywords": ["ETF", "交易型开放式指数基金", "指数基金", "被动投资"],
        "category": "基金类型"
    },
    {
        "id": "k008",
        "title": "基金定投是什么？有什么优势？",
        "content": "基金定投是指投资者在固定时间以固定金额投资基金的方式。其优势包括：1）平均成本法，降低投资成本；2）分散投资时点风险；3）培养良好的投资习惯；4）适合长期投资；5）门槛低，适合普通投资者；6）可以克服择时困难和情绪波动。基金定投特别适合波动较大的权益类基金。",
        "keywords": ["基金定投", "定期定额", "平均成本", "长期投资", "分散风险"],
        "category": "投资策略"
    },
    {
        "id": "k009",
        "title": "什么是基金的分红方式？",
        "content": "基金分红是指基金将收益的一部分派发给投资者。分红方式主要有两种：1）现金分红：直接将分红金额发放给投资者；2）红利再投资：将分红金额自动转为基金份额。投资者可以根据自己的需求选择分红方式。现金分红适合需要现金流的投资者，红利再投资适合追求长期复利增长的投资者。",
        "keywords": ["基金分红", "现金分红", "红利再投资", "收益分配", "复利"],
        "category": "基金收益"
    },
    {
        "id": "k010",
        "title": "如何评估基金的表现？",
        "content": "评估基金表现的指标包括：1）收益率：绝对收益和相对基准的超额收益；2）风险调整收益指标：夏普比率、特雷诺比率、詹森指数等；3）最大回撤：衡量基金下跌风险；4）波动率：衡量基金价格波动程度；5）信息比率：衡量基金经理的主动管理能力；6）业绩持续性：基金业绩的稳定性。投资者应综合考虑这些指标。",
        "keywords": ["基金评估", "收益率", "夏普比率", "最大回撤", "波动率", "信息比率", "业绩持续性"],
        "category": "基金评估"
    }
]

# 工具处理程序
async def tool_handler(response, conversation):
    """
    处理工具调用
    
    参数:
    - provider_type: 提供者类型
    - response: 响应
    - conversation: 对话历史
    
    返回:
    - 工具调用结果
    """
    from multi_agent_orchestrator.types import ConversationMessage, ParticipantRole
    
    response_content_blocks = response.content
    
    # 初始化空的工具结果列表
    tool_results = []
    
    if not response_content_blocks:
        raise ValueError("No content blocks in response")
    
    for content_block in response_content_blocks:
        if "text" in content_block:
            # 处理文本内容（如果需要）
            pass
        
        if "toolUse" in content_block:
            tool_use_block = content_block["toolUse"]
            tool_use_name = tool_use_block.get("name")
            
            if tool_use_name == "query_nebula_knowledge_graph":
                tool_response = await query_nebula_knowledge_graph(
                    tool_use_block["input"].get("query", "")
                )
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_block["toolUseId"],
                        "content": [{"text": tool_response}],
                    }
                })
            elif tool_use_name == "query_opensearch_knowledge":
                tool_response = await query_opensearch_knowledge(
                    tool_use_block["input"].get("query", ""),
                    tool_use_block["input"].get("size", 5)
                )
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_block["toolUseId"],
                        "content": [{"text": tool_response}],
                    }
                })
            elif tool_use_name == "query_dynamodb_user_info":
                tool_response = await query_dynamodb_user_info(
                    tool_use_block["input"].get("user_id", "")
                )
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_block["toolUseId"],
                        "content": [{"text": tool_response}],
                    }
                })
            elif tool_use_name == "update_dynamodb_user_info":
                tool_response = await update_dynamodb_user_info(
                    tool_use_block["input"].get("user_id", ""),
                    tool_use_block["input"].get("user_info", {}),
                    tool_use_block["input"].get("risk_profile", "")
                )
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_block["toolUseId"],
                        "content": [{"text": tool_response}],
                    }
                })
            elif tool_use_name == "search_financial_info":
                tool_response = await search_financial_info(
                    tool_use_block["input"].get("query", ""),
                    tool_use_block["input"].get("num_results", 5)
                )
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_block["toolUseId"],
                        "content": [{"text": tool_response}],
                    }
                })
    
    # 将工具结果嵌入到新的用户消息中
    message = ConversationMessage(
        role=ParticipantRole.USER.value,
        content=tool_results
    )
    
    return message

# 查询Nebula知识图谱
async def query_nebula_knowledge_graph(query: str) -> str:
    """
    查询Nebula知识图谱，获取基金相关信息
    
    参数:
    - query: 查询语句，使用nGQL语法
    
    返回:
    - 查询结果（字符串格式）
    """
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    # 模拟查询处理
    # 这里我们根据查询语句中的关键词来返回模拟数据
    
    # 解析查询语句，提取关键信息
    query = query.lower()
    
    # 初始化结果
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "results": []
    }
    
    # 根据查询类型返回不同的结果
    if "match (f:fund)" in query:
        # 基金查询
        risk_level = None
        fund_type = None
        
        # 提取风险等级
        if "risk_level" in query:
            for level in ["保守型", "稳健型", "平衡型", "成长型", "进取型"]:
                if level in query:
                    risk_level = level
                    break
        
        # 提取基金类型
        if "fund_type" in query:
            for ftype in ["股票型", "债券型", "混合型", "指数型", "货币型"]:
                if ftype in query:
                    fund_type = ftype
                    break
        
        # 根据条件筛选基金
        filtered_funds = []
        for fund_id, fund in fund_data.items():
            if risk_level and fund["risk_level"] != risk_level:
                continue
            if fund_type and fund["fund_type"] != fund_type:
                continue
            filtered_funds.append({
                "fund_id": fund_id,
                "fund_name": fund["fund_name"],
                "fund_type": fund["fund_type"],
                "risk_level": fund["risk_level"],
                "nav": fund["nav"],
                "annual_return_1y": fund["annual_return"]["1y"]
            })
        
        result["results"] = filtered_funds
    
    elif "match (f:fund)-[:belongs_to]->(c:category)" in query:
        # 基金分类查询
        categories = {
            "股票型": [],
            "债券型": [],
            "混合型": [],
            "指数型": [],
            "货币型": []
        }
        
        for fund_id, fund in fund_data.items():
            if fund["fund_type"] in categories:
                categories[fund["fund_type"]].append({
                    "fund_id": fund_id,
                    "fund_name": fund["fund_name"]
                })
        
        result["results"] = categories
    
    elif "match (f:fund)-[:has_performance]->(p:performance)" in query:
        # 基金业绩查询
        performances = []
        
        for fund_id, fund in fund_data.items():
            performances.append({
                "fund_id": fund_id,
                "fund_name": fund["fund_name"],
                "annual_return_1y": fund["annual_return"]["1y"],
                "annual_return_3y": fund["annual_return"]["3y"],
                "annual_return_5y": fund["annual_return"]["5y"],
                "volatility": fund["volatility"],
                "sharpe_ratio": fund["sharpe_ratio"],
                "max_drawdown": fund["max_drawdown"]
            })
        
        result["results"] = performances
    
    elif "match (f:fund {fund_id:" in query:
        # 特定基金查询
        fund_id = None
        for fid in fund_data.keys():
            if fid in query:
                fund_id = fid
                break
        
        if fund_id and fund_id in fund_data:
            result["results"] = [fund_data[fund_id]]
        else:
            result["status"] = "error"
            result["message"] = "未找到指定基金"
    
    else:
        # 默认返回所有基金的基本信息
        all_funds = []
        for fund_id, fund in fund_data.items():
            all_funds.append({
                "fund_id": fund_id,
                "fund_name": fund["fund_name"],
                "fund_type": fund["fund_type"],
                "risk_level": fund["risk_level"]
            })
        
        result["results"] = all_funds
    
    # 将结果转换为格式化的字符串
    result_str = f"""
Nebula知识图谱查询结果
时间戳: {result['timestamp']}
查询: {result['query']}
状态: {result['status']}

查询结果:
{json.dumps(result['results'], ensure_ascii=False, indent=2)}
"""
    
    return result_str

# 查询OpenSearch金融知识
async def query_opensearch_knowledge(query: str, size: int = 5) -> str:
    """
    查询OpenSearch金融知识库，获取金融和基金相关知识
    
    参数:
    - query: 查询关键词或短语
    - size: 返回结果数量，默认为5
    
    返回:
    - 查询结果（字符串格式）
    """
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    # 模拟查询处理
    # 这里我们根据查询关键词来匹配模拟数据
    
    # 初始化结果
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "total_hits": 0,
        "results": []
    }
    
    # 根据关键词匹配知识条目
    matched_items = []
    query_terms = query.lower().split()
    
    for item in financial_knowledge:
        score = 0
        # 检查标题匹配
        if query.lower() in item["title"].lower():
            score += 10
        
        # 检查内容匹配
        if query.lower() in item["content"].lower():
            score += 5
        
        # 检查关键词匹配
        for term in query_terms:
            if term in item["title"].lower():
                score += 3
            if term in item["content"].lower():
                score += 1
            for keyword in item["keywords"]:
                if term in keyword.lower():
                    score += 2
        
        if score > 0:
            matched_items.append((item, score))
    
    # 按匹配分数排序
    matched_items.sort(key=lambda x: x[1], reverse=True)
    
    # 限制返回结果数量
    result["total_hits"] = len(matched_items)
    result["results"] = [item[0] for item in matched_items[:size]]
    
    # 将结果转换为格式化的字符串
    result_str = f"""
OpenSearch金融知识查询结果
时间戳: {result['timestamp']}
查询: {result['query']}
总匹配数: {result['total_hits']}

查询结果:
"""
    
    for i, item in enumerate(result["results"], 1):
        result_str += f"""
{i}. {item['title']}
分类: {item['category']}
关键词: {', '.join(item['keywords'])}
内容: {item['content']}
"""
    
    return result_str

# 查询DynamoDB用户信息
async def query_dynamodb_user_info(user_id: str) -> str:
    """
    查询DynamoDB中的用户基本信息
    
    参数:
    - user_id: 用户ID
    
    返回:
    - 用户信息（字符串格式）
    """
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    # 初始化结果
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id
    }
    
    # 检查用户是否存在
    if user_id in user_data:
        result["user_info"] = user_data[user_id]["user_info"]
        result["risk_profile"] = user_data[user_id]["risk_profile"]
        result["investment_preferences"] = user_data[user_id]["investment_preferences"]
        result["portfolio"] = user_data[user_id]["portfolio"]
    else:
        result["status"] = "error"
        result["message"] = f"未找到用户ID为 {user_id} 的用户信息"
    
    # 将结果转换为格式化的字符串
    if result["status"] == "success":
        user_info = result["user_info"]
        risk_profile = result["risk_profile"]
        investment_preferences = result["investment_preferences"]
        portfolio = result["portfolio"]
        
        result_str = f"""
DynamoDB用户信息查询结果
时间戳: {result['timestamp']}
用户ID: {result['user_id']}
状态: {result['status']}

用户基本信息:
- 姓名: {user_info['name']}
- 年龄: {user_info['age']}
- 性别: {user_info['gender']}
- 职业: {user_info['occupation']}
- 年收入: {user_info['annual_income']}元
- 投资经验: {user_info['investment_experience']}年
- 学历: {user_info['education']}
- 金融资产: {user_info['financial_assets']}元
- 投资期限: {user_info['investment_horizon']}年
- 投资目标: {user_info['investment_goal']}

风险偏好: {risk_profile}

投资偏好:
- 偏好基金类型: {', '.join(investment_preferences['preferred_fund_types'])}
- 避开行业: {', '.join(investment_preferences['avoid_industries']) if investment_preferences['avoid_industries'] else '无'}
- ESG偏好: {'是' if investment_preferences['esg_preference'] else '否'}
- 分红偏好: {'是' if investment_preferences['dividend_preference'] else '否'}

当前投资组合:
"""
        
        for item in portfolio:
            fund_id = item["fund_id"]
            amount = item["amount"]
            fund_name = fund_data[fund_id]["fund_name"] if fund_id in fund_data else "未知基金"
            result_str += f"- {fund_name} ({fund_id}): {amount}元\n"
    else:
        result_str = f"""
DynamoDB用户信息查询结果
时间戳: {result['timestamp']}
用户ID: {result['user_id']}
状态: {result['status']}
消息: {result['message']}
"""
    
    return result_str

# 更新DynamoDB用户信息
async def update_dynamodb_user_info(user_id: str, user_info: Dict[str, Any], risk_profile: str = None) -> str:
    """
    更新DynamoDB中的用户基本信息
    
    参数:
    - user_id: 用户ID
    - user_info: 用户信息，包括姓名、年龄、收入、投资经验等
    - risk_profile: 用户风险偏好，可以是保守型、稳健型、平衡型、成长型、进取型
    
    返回:
    - 更新结果（字符串格式）
    """
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    # 初始化结果
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "updated_fields": []
    }
    
    # 检查用户是否存在，如果不存在则创建
    if user_id not in user_data:
        user_data[user_id] = {
            "user_info": {},
            "risk_profile": risk_profile if risk_profile else "平衡型",
            "investment_preferences": {
                "preferred_fund_types": [],
                "avoid_industries": [],
                "esg_preference": False,
                "dividend_preference": False
            },
            "portfolio": []
        }
        result["message"] = f"创建了新用户 {user_id}"
    
    # 更新用户信息
    if user_info:
        for key, value in user_info.items():
            user_data[user_id]["user_info"][key] = value
            result["updated_fields"].append(f"user_info.{key}")
    
    # 更新风险偏好
    if risk_profile:
        valid_risk_profiles = ["保守型", "稳健型", "平衡型", "成长型", "进取型"]
        if risk_profile in valid_risk_profiles:
            user_data[user_id]["risk_profile"] = risk_profile
            result["updated_fields"].append("risk_profile")
        else:
            result["status"] = "warning"
            result["message"] = f"无效的风险偏好 '{risk_profile}'，有效值为: {', '.join(valid_risk_profiles)}"
    
    # 将结果转换为格式化的字符串
    result_str = f"""
DynamoDB用户信息更新结果
时间戳: {result['timestamp']}
用户ID: {result['user_id']}
状态: {result['status']}
更新字段: {', '.join(result['updated_fields']) if result['updated_fields'] else '无'}
"""
    
    if "message" in result:
        result_str += f"消息: {result['message']}\n"
    
    return result_str

# 搜索金融信息
async def search_financial_info(query: str, num_results: int = 5) -> str:
    """
    使用搜索引擎查询最新的金融信息
    
    参数:
    - query: 搜索关键词或短语
    - num_results: 返回结果数量，默认为5
    
    返回:
    - 搜索结果（字符串格式）
    """
    # 模拟API调用延迟
    await asyncio.sleep(1.0)
    
    # 模拟搜索结果
    search_results = [
        {
            "title": f"{query}相关的最新市场动态",
            "snippet": f"最新的{query}市场分析显示，近期市场波动加剧，投资者需要关注央行政策和经济数据。专家建议保持多元化投资策略，控制风险敞口。",
            "url": f"https://example.com/finance/{query.replace(' ', '-')}-market-analysis",
            "date": "2025-04-02"
        },
        {
            "title": f"{query}投资策略指南",
            "snippet": f"本文提供了关于{query}的详细投资策略，包括市场趋势分析、风险评估和投资建议。适合不同风险偏好的投资者参考。",
            "url": f"https://example.com/investment/{query.replace(' ', '-')}-strategy",
            "date": "2025-03-28"
        },
        {
            "title": f"专家解读：{query}未来发展趋势",
            "snippet": f"金融专家对{query}的未来发展进行了深入解读，分析了影响因素和可能的发展路径。投资者可以据此调整投资组合。",
            "url": f"https://example.com/expert/{query.replace(' ', '-')}-future-trends",
            "date": "2025-03-25"
        },
        {
            "title": f"{query}相关政策解析",
            "snippet": f"近期出台的与{query}相关的政策可能对市场产生重大影响。本文详细解析了政策内容及其对投资者的影响。",
            "url": f"https://example.com/policy/{query.replace(' ', '-')}-analysis",
            "date": "2025-03-20"
        },
        {
            "title": f"{query}风险管理指南",
            "snippet": f"在投资{query}时，风险管理至关重要。本文提供了实用的风险管理策略，帮助投资者保护资产并获取稳定收益。",
            "url": f"https://example.com/risk/{query.replace(' ', '-')}-management",
            "date": "2025-03-15"
        },
        {
            "title": f"{query}投资案例分析",
            "snippet": f"通过分析成功和失败的{query}投资案例，本文总结了宝贵的经验教训，为投资者提供实践参考。",
            "url": f"https://example.com/cases/{query.replace(' ', '-')}-studies",
            "date": "2025-03-10"
        },
        {
            "title": f"{query}市场数据分析",
            "snippet": f"基于最新的市场数据，本文对{query}进行了全面分析，包括价格趋势、交易量变化和市场情绪指标。",
            "url": f"https://example.com/data/{query.replace(' ', '-')}-analysis",
            "date": "2025-03-05"
        }
    ]
    
    # 限制结果数量
    limited_results = search_results[:min(num_results, len(search_results))]
    
    # 构建结果字符串
    result_str = f"""
金融信息搜索结果
时间戳: {datetime.now().isoformat()}
查询: {query}
结果数量: {len(limited_results)}

搜索结果:
"""
    
    for i, result in enumerate(limited_results, 1):
        result_str += f"""
{i}. {result['title']}
   日期: {result['date']}
   摘要: {result['snippet']}
   链接: {result['url']}
"""
    
    return result_str
