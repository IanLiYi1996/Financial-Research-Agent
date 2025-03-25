from typing import Dict, List, Any
import asyncio
import json
import random
from datetime import datetime

# 技术指标分析工具描述
technical_indicator_description = [{
    "toolSpec": {
        "name": "technical_indicator_analysis",
        "description": "分析指定资产的技术指标，包括RSI、MACD、移动平均线等",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "资产代码，如BTC、AAPL、EUR/USD等"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "时间周期，如1d（日）、4h（4小时）、1h（小时）、15m（15分钟）等"
                    }
                },
                "required": ["symbol"]
            }
        }
    }
}]

# 市场动态注释工具描述
market_dynamics_description = [{
    "toolSpec": {
        "name": "market_dynamics_annotation",
        "description": "分析市场动态并提供注释，包括波动性、趋势、成交量等",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "资产代码，如BTC、AAPL、EUR/USD等"
                    }
                },
                "required": ["symbol"]
            }
        }
    }
}]

# 新闻分析工具描述
news_analysis_description = [{
    "toolSpec": {
        "name": "news_analysis",
        "description": "分析与特定资产相关的新闻，评估市场情绪和潜在影响",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "资产代码，如BTC、AAPL、EUR/USD等"
                    },
                    "days": {
                        "type": "number",
                        "description": "分析最近几天的新闻，默认为3天"
                    }
                },
                "required": ["symbol"]
            }
        }
    }
}]

# 模拟市场数据
market_data = {
    # 加密货币
    "BTC": {
        "price": 65000,
        "change_24h": 2.5,
        "volume_24h": 45000000000,
        "market_cap": 1200000000000,
        "rsi": 58,
        "macd": "bullish",
        "moving_averages": {
            "MA_50": "uptrend",
            "MA_200": "uptrend",
            "EMA_20": "uptrend"
        },
        "support_levels": [62000, 60000, 58000],
        "resistance_levels": [66000, 68000, 70000],
        "volatility": "medium",
        "trend": "bullish",
        "volume_trend": "increasing"
    },
    "ETH": {
        "price": 3500,
        "change_24h": 1.8,
        "volume_24h": 20000000000,
        "market_cap": 420000000000,
        "rsi": 55,
        "macd": "neutral",
        "moving_averages": {
            "MA_50": "uptrend",
            "MA_200": "uptrend",
            "EMA_20": "neutral"
        },
        "support_levels": [3300, 3200, 3000],
        "resistance_levels": [3600, 3800, 4000],
        "volatility": "medium",
        "trend": "neutral",
        "volume_trend": "stable"
    },
    
    # 股票
    "AAPL": {
        "price": 175.5,
        "change_24h": 0.8,
        "volume_24h": 65000000,
        "market_cap": 2800000000000,
        "rsi": 62,
        "macd": "bullish",
        "moving_averages": {
            "MA_50": "uptrend",
            "MA_200": "uptrend",
            "EMA_20": "uptrend"
        },
        "support_levels": [172, 170, 165],
        "resistance_levels": [178, 180, 185],
        "volatility": "low",
        "trend": "bullish",
        "volume_trend": "stable"
    },
    "MSFT": {
        "price": 410.2,
        "change_24h": 1.2,
        "volume_24h": 25000000,
        "market_cap": 3050000000000,
        "rsi": 65,
        "macd": "bullish",
        "moving_averages": {
            "MA_50": "uptrend",
            "MA_200": "uptrend",
            "EMA_20": "uptrend"
        },
        "support_levels": [405, 400, 395],
        "resistance_levels": [415, 420, 425],
        "volatility": "low",
        "trend": "bullish",
        "volume_trend": "increasing"
    },
    
    # 指数
    "DJ30": {
        "price": 38500,
        "change_24h": 0.5,
        "volume_24h": None,
        "market_cap": None,
        "rsi": 60,
        "macd": "neutral",
        "moving_averages": {
            "MA_50": "uptrend",
            "MA_200": "uptrend",
            "EMA_20": "neutral"
        },
        "support_levels": [38000, 37500, 37000],
        "resistance_levels": [39000, 39500, 40000],
        "volatility": "low",
        "trend": "neutral",
        "volume_trend": "stable"
    },
    "S&P500": {
        "price": 5100,
        "change_24h": 0.3,
        "volume_24h": None,
        "market_cap": None,
        "rsi": 58,
        "macd": "neutral",
        "moving_averages": {
            "MA_50": "uptrend",
            "MA_200": "uptrend",
            "EMA_20": "neutral"
        },
        "support_levels": [5050, 5000, 4950],
        "resistance_levels": [5150, 5200, 5250],
        "volatility": "low",
        "trend": "neutral",
        "volume_trend": "stable"
    },
    
    # 外汇
    "EUR/USD": {
        "price": 1.0850,
        "change_24h": -0.2,
        "volume_24h": None,
        "market_cap": None,
        "rsi": 45,
        "macd": "bearish",
        "moving_averages": {
            "MA_50": "downtrend",
            "MA_200": "neutral",
            "EMA_20": "downtrend"
        },
        "support_levels": [1.0800, 1.0750, 1.0700],
        "resistance_levels": [1.0900, 1.0950, 1.1000],
        "volatility": "low",
        "trend": "bearish",
        "volume_trend": "stable"
    },
    "USD/JPY": {
        "price": 151.50,
        "change_24h": 0.1,
        "volume_24h": None,
        "market_cap": None,
        "rsi": 55,
        "macd": "neutral",
        "moving_averages": {
            "MA_50": "uptrend",
            "MA_200": "uptrend",
            "EMA_20": "neutral"
        },
        "support_levels": [150.50, 150.00, 149.50],
        "resistance_levels": [152.00, 152.50, 153.00],
        "volatility": "medium",
        "trend": "neutral",
        "volume_trend": "stable"
    }
}

# 模拟新闻数据
news_data = {
    "BTC": [
        {"title": "比特币突破65,000美元，创近期新高", "date": "2025-03-24", "sentiment": "positive", "impact": "high"},
        {"title": "大型机构投资者增持比特币，市场信心增强", "date": "2025-03-23", "sentiment": "positive", "impact": "medium"},
        {"title": "分析师预测比特币年内有望突破80,000美元", "date": "2025-03-22", "sentiment": "positive", "impact": "medium"},
        {"title": "比特币网络哈希率创历史新高，安全性进一步增强", "date": "2025-03-21", "sentiment": "positive", "impact": "low"},
        {"title": "监管机构考虑对加密货币实施新规定", "date": "2025-03-20", "sentiment": "negative", "impact": "medium"}
    ],
    "ETH": [
        {"title": "以太坊网络升级成功，交易费用显著降低", "date": "2025-03-24", "sentiment": "positive", "impact": "high"},
        {"title": "以太坊DeFi生态系统总锁仓价值突破1000亿美元", "date": "2025-03-23", "sentiment": "positive", "impact": "medium"},
        {"title": "以太坊开发者宣布新功能路线图", "date": "2025-03-22", "sentiment": "positive", "impact": "medium"},
        {"title": "大型企业开始在以太坊网络上构建应用", "date": "2025-03-21", "sentiment": "positive", "impact": "medium"},
        {"title": "以太坊面临新的竞争对手挑战", "date": "2025-03-20", "sentiment": "negative", "impact": "low"}
    ],
    "AAPL": [
        {"title": "苹果公司宣布新一代iPhone发布日期", "date": "2025-03-24", "sentiment": "positive", "impact": "high"},
        {"title": "苹果服务业务收入创历史新高", "date": "2025-03-23", "sentiment": "positive", "impact": "medium"},
        {"title": "分析师上调苹果目标价", "date": "2025-03-22", "sentiment": "positive", "impact": "medium"},
        {"title": "苹果扩大在印度的生产规模", "date": "2025-03-21", "sentiment": "positive", "impact": "low"},
        {"title": "苹果面临新的反垄断调查", "date": "2025-03-20", "sentiment": "negative", "impact": "medium"}
    ],
    "MSFT": [
        {"title": "微软云业务增长超预期", "date": "2025-03-24", "sentiment": "positive", "impact": "high"},
        {"title": "微软扩大AI投资规模", "date": "2025-03-23", "sentiment": "positive", "impact": "medium"},
        {"title": "微软与OpenAI深化合作关系", "date": "2025-03-22", "sentiment": "positive", "impact": "medium"},
        {"title": "微软宣布新的企业解决方案", "date": "2025-03-21", "sentiment": "positive", "impact": "low"},
        {"title": "微软面临数据隐私质疑", "date": "2025-03-20", "sentiment": "negative", "impact": "low"}
    ],
    "DJ30": [
        {"title": "道琼斯指数小幅上涨，市场情绪谨慎乐观", "date": "2025-03-24", "sentiment": "positive", "impact": "medium"},
        {"title": "美联储暗示可能降息，道指受益", "date": "2025-03-23", "sentiment": "positive", "impact": "high"},
        {"title": "企业财报季表现超预期，提振道指", "date": "2025-03-22", "sentiment": "positive", "impact": "medium"},
        {"title": "经济数据向好，道指创新高", "date": "2025-03-21", "sentiment": "positive", "impact": "medium"},
        {"title": "通胀担忧再起，道指承压", "date": "2025-03-20", "sentiment": "negative", "impact": "medium"}
    ],
    "S&P500": [
        {"title": "标普500指数创历史新高", "date": "2025-03-24", "sentiment": "positive", "impact": "high"},
        {"title": "科技股领涨标普500", "date": "2025-03-23", "sentiment": "positive", "impact": "medium"},
        {"title": "标普500指数估值处于历史高位", "date": "2025-03-22", "sentiment": "neutral", "impact": "low"},
        {"title": "分析师预测标普500年内有望突破5500点", "date": "2025-03-21", "sentiment": "positive", "impact": "medium"},
        {"title": "市场波动性增加，标普500面临调整风险", "date": "2025-03-20", "sentiment": "negative", "impact": "medium"}
    ],
    "EUR/USD": [
        {"title": "欧元兑美元汇率下跌，美元指数走强", "date": "2025-03-24", "sentiment": "negative", "impact": "medium"},
        {"title": "欧洲央行维持利率不变，欧元承压", "date": "2025-03-23", "sentiment": "negative", "impact": "high"},
        {"title": "美国经济数据强劲，美元走高", "date": "2025-03-22", "sentiment": "negative", "impact": "medium"},
        {"title": "欧元区通胀数据低于预期", "date": "2025-03-21", "sentiment": "negative", "impact": "medium"},
        {"title": "分析师预测欧元兑美元将在年内反弹", "date": "2025-03-20", "sentiment": "positive", "impact": "low"}
    ],
    "USD/JPY": [
        {"title": "美元兑日元汇率保持稳定", "date": "2025-03-24", "sentiment": "neutral", "impact": "low"},
        {"title": "日本央行暗示可能进一步收紧货币政策", "date": "2025-03-23", "sentiment": "positive", "impact": "medium"},
        {"title": "美日利差维持高位，支撑美元兑日元", "date": "2025-03-22", "sentiment": "positive", "impact": "medium"},
        {"title": "日本通胀数据高于预期", "date": "2025-03-21", "sentiment": "negative", "impact": "medium"},
        {"title": "地缘政治风险增加，日元避险需求上升", "date": "2025-03-20", "sentiment": "negative", "impact": "medium"}
    ]
}

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
            
            if tool_use_name == "technical_indicator_analysis":
                tool_response = await technical_indicator_analysis(
                    tool_use_block["input"].get("symbol", ""),
                    tool_use_block["input"].get("timeframe", "1d")
                )
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_block["toolUseId"],
                        "content": [{"text": tool_response}],
                    }
                })
            elif tool_use_name == "market_dynamics_annotation":
                tool_response = await market_dynamics_annotation(
                    tool_use_block["input"].get("symbol", "")
                )
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_block["toolUseId"],
                        "content": [{"text": tool_response}],
                    }
                })
            elif tool_use_name == "news_analysis":
                tool_response = await news_analysis(
                    tool_use_block["input"].get("symbol", ""),
                    tool_use_block["input"].get("days", 3)
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

# 技术指标分析工具
async def technical_indicator_analysis(symbol: str, timeframe: str = "1d") -> str:
    """
    分析指定资产的技术指标
    
    参数:
    - symbol: 资产代码，如BTC、AAPL、EUR/USD等
    - timeframe: 时间周期，如1d（日）、4h（4小时）、1h（小时）、15m（15分钟）等
    
    返回:
    - 技术指标分析结果（字符串格式）
    """
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    # 检查资产是否存在
    if symbol not in market_data:
        return f"未找到资产 {symbol} 的数据。时间戳: {datetime.now().isoformat()}"
    
    # 获取资产数据
    asset_data = market_data[symbol]
    
    # 构建分析结果
    result_dict = {
        "symbol": symbol,
        "timeframe": timeframe,
        "timestamp": datetime.now().isoformat(),
        "price": asset_data["price"],
        "change_24h": asset_data["change_24h"],
        "technical_indicators": {
            "rsi": asset_data["rsi"],
            "macd": asset_data["macd"],
            "moving_averages": asset_data["moving_averages"]
        },
        "support_levels": asset_data["support_levels"],
        "resistance_levels": asset_data["resistance_levels"],
        "analysis_summary": get_technical_analysis_summary(asset_data)
    }
    
    # 将字典转换为格式化的字符串
    result_str = f"""
技术指标分析结果 - {symbol} ({timeframe})
时间戳: {result_dict['timestamp']}
当前价格: {result_dict['price']}
24小时变化: {result_dict['change_24h']}%

技术指标:
- RSI: {result_dict['technical_indicators']['rsi']}
- MACD: {result_dict['technical_indicators']['macd']}
- 移动平均线:
  * 50日均线: {result_dict['technical_indicators']['moving_averages']['MA_50']}
  * 200日均线: {result_dict['technical_indicators']['moving_averages']['MA_200']}
  * 20日指数均线: {result_dict['technical_indicators']['moving_averages']['EMA_20']}

支撑位: {', '.join(str(level) for level in result_dict['support_levels'])}
阻力位: {', '.join(str(level) for level in result_dict['resistance_levels'])}

分析摘要: {result_dict['analysis_summary']}
"""
    
    return result_str

# 市场动态注释工具
async def market_dynamics_annotation(symbol: str) -> str:
    """
    分析市场动态并提供注释
    
    参数:
    - symbol: 资产代码，如BTC、AAPL、EUR/USD等
    
    返回:
    - 市场动态分析结果（字符串格式）
    """
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    # 检查资产是否存在
    if symbol not in market_data:
        return f"未找到资产 {symbol} 的数据。时间戳: {datetime.now().isoformat()}"
    
    # 获取资产数据
    asset_data = market_data[symbol]
    
    # 获取分析数据
    volatility = asset_data["volatility"]
    trend = asset_data["trend"]
    volume_trend = asset_data["volume_trend"]
    market_sentiment = get_market_sentiment(asset_data)
    risk_level = get_risk_level(asset_data)
    analysis_summary = get_market_dynamics_summary(asset_data, symbol)
    
    # 构建分析结果字符串
    result_str = f"""
市场动态分析 - {symbol}
时间戳: {datetime.now().isoformat()}

市场动态:
- 波动性: {volatility}
- 趋势: {trend}
- 成交量趋势: {volume_trend}

市场情绪: {market_sentiment}
风险水平: {risk_level}

分析摘要: {analysis_summary}
"""
    
    return result_str

# 新闻分析工具
async def news_analysis(symbol: str, days: int = 3) -> str:
    """
    分析与特定资产相关的新闻
    
    参数:
    - symbol: 资产代码，如BTC、AAPL、EUR/USD等
    - days: 分析最近几天的新闻，默认为3天
    
    返回:
    - 新闻分析结果（字符串格式）
    """
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    # 检查资产是否存在
    if symbol not in news_data:
        return f"未找到资产 {symbol} 的新闻数据。时间戳: {datetime.now().isoformat()}"
    
    # 获取资产新闻数据
    asset_news = news_data[symbol]
    
    # 限制天数
    recent_news = asset_news[:days]
    
    # 分析新闻情绪
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    impact_counts = {"high": 0, "medium": 0, "low": 0}
    
    for news in recent_news:
        sentiment_counts[news["sentiment"]] += 1
        impact_counts[news["impact"]] += 1
    
    # 确定主要情绪
    if sentiment_counts["positive"] > sentiment_counts["negative"]:
        main_sentiment = "积极"
    elif sentiment_counts["positive"] < sentiment_counts["negative"]:
        main_sentiment = "消极"
    else:
        main_sentiment = "中性"
    
    # 构建新闻列表字符串
    news_list_str = ""
    for i, news in enumerate(recent_news, 1):
        news_list_str += f"{i}. {news['date']} - {news['title']} (情绪: {news['sentiment']}, 影响: {news['impact']})\n"
    
    # 构建分析结果字符串
    result_str = f"""
新闻分析结果 - {symbol}
时间戳: {datetime.now().isoformat()}
分析天数: {days}
新闻数量: {len(recent_news)}

新闻列表:
{news_list_str}

情绪分析:
- 主要情绪: {main_sentiment}
- 积极新闻: {sentiment_counts["positive"]}
- 中性新闻: {sentiment_counts["neutral"]}
- 消极新闻: {sentiment_counts["negative"]}

影响分布:
- 高影响: {impact_counts["high"]}
- 中等影响: {impact_counts["medium"]}
- 低影响: {impact_counts["low"]}

分析摘要: {get_news_analysis_summary(recent_news, symbol)}
"""
    
    return result_str

# 辅助函数：获取技术分析摘要
def get_technical_analysis_summary(asset_data: Dict[str, Any]) -> str:
    """生成技术分析摘要"""
    rsi = asset_data["rsi"]
    macd = asset_data["macd"]
    ma_50 = asset_data["moving_averages"]["MA_50"]
    ma_200 = asset_data["moving_averages"]["MA_200"]
    
    if rsi > 70:
        rsi_status = "超买"
    elif rsi < 30:
        rsi_status = "超卖"
    else:
        rsi_status = "中性"
    
    if macd == "bullish" and ma_50 == "uptrend" and ma_200 == "uptrend":
        return f"技术指标整体看涨。RSI为{rsi}，处于{rsi_status}状态；MACD看涨；50日和200日移动平均线均呈上升趋势。建议关注上方阻力位。"
    elif macd == "bearish" and ma_50 == "downtrend" and ma_200 == "downtrend":
        return f"技术指标整体看跌。RSI为{rsi}，处于{rsi_status}状态；MACD看跌；50日和200日移动平均线均呈下降趋势。建议关注下方支撑位。"
    else:
        return f"技术指标呈现混合信号。RSI为{rsi}，处于{rsi_status}状态；MACD为{macd}；50日移动平均线呈{ma_50}趋势，200日移动平均线呈{ma_200}趋势。建议保持谨慎，等待更明确的信号。"

# 辅助函数：获取市场情绪
def get_market_sentiment(asset_data: Dict[str, Any]) -> str:
    """根据资产数据确定市场情绪"""
    trend = asset_data["trend"]
    volatility = asset_data["volatility"]
    
    if trend == "bullish" and volatility != "high":
        return "乐观"
    elif trend == "bearish" and volatility != "high":
        return "悲观"
    elif trend == "neutral" and volatility == "low":
        return "谨慎中性"
    elif volatility == "high":
        return "不确定性高"
    else:
        return "中性"

# 辅助函数：获取风险水平
def get_risk_level(asset_data: Dict[str, Any]) -> str:
    """根据资产数据确定风险水平"""
    volatility = asset_data["volatility"]
    trend = asset_data["trend"]
    rsi = asset_data["rsi"]
    
    if volatility == "high" or rsi > 75 or rsi < 25:
        return "高"
    elif volatility == "medium" or (rsi > 65 or rsi < 35):
        return "中"
    else:
        return "低"

# 辅助函数：获取市场动态摘要
def get_market_dynamics_summary(asset_data: Dict[str, Any], symbol: str) -> str:
    """生成市场动态摘要"""
    volatility = asset_data["volatility"]
    trend = asset_data["trend"]
    volume_trend = asset_data["volume_trend"]
    
    if trend == "bullish" and volume_trend == "increasing":
        return f"{symbol}市场呈现强劲上升趋势，成交量增加，表明买方力量强劲。市场波动性{volatility}，建议关注上方阻力位突破机会。"
    elif trend == "bullish" and volume_trend != "increasing":
        return f"{symbol}市场呈现上升趋势，但成交量{volume_trend}，可能表明上涨动能不足。市场波动性{volatility}，建议谨慎追高。"
    elif trend == "bearish" and volume_trend == "increasing":
        return f"{symbol}市场呈现明显下降趋势，成交量增加，表明卖方力量强劲。市场波动性{volatility}，建议关注下方支撑位。"
    elif trend == "bearish" and volume_trend != "increasing":
        return f"{symbol}市场呈现下降趋势，但成交量{volume_trend}，可能表明下跌动能减弱。市场波动性{volatility}，建议关注可能的反弹信号。"
    else:
        return f"{symbol}市场呈现{trend}趋势，成交量{volume_trend}，波动性{volatility}。市场方向不明确，建议等待更清晰的信号。"

# 辅助函数：获取新闻分析摘要
def get_news_analysis_summary(news_items: List[Dict[str, Any]], symbol: str) -> str:
    """生成新闻分析摘要"""
    if not news_items:
        return f"未找到与{symbol}相关的最新新闻。"
    
    # 计算情绪分布
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    high_impact_news = []
    
    for news in news_items:
        sentiment_counts[news["sentiment"]] += 1
        if news["impact"] == "high":
            high_impact_news.append(news)
    
    # 确定主要情绪
    if sentiment_counts["positive"] > sentiment_counts["negative"]:
        main_sentiment = "积极"
    elif sentiment_counts["positive"] < sentiment_counts["negative"]:
        main_sentiment = "消极"
    else:
        main_sentiment = "中性"
    
    # 生成摘要
    summary = f"最近关于{symbol}的新闻整体情绪{main_sentiment}。"
    
    if high_impact_news:
        summary += f" 主要高影响力新闻包括："
        for i, news in enumerate(high_impact_news[:2], 1):
            summary += f" {i}. {news['title']}；"
    
    if sentiment_counts["positive"] > 0:
        summary += f" 有{sentiment_counts['positive']}条积极新闻，"
    if sentiment_counts["negative"] > 0:
        summary += f" 有{sentiment_counts['negative']}条消极新闻，"
    if sentiment_counts["neutral"] > 0:
        summary += f" 有{sentiment_counts['neutral']}条中性新闻。"
    
    return summary
