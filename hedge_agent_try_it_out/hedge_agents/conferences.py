"""
HedgeAgents会议系统

实现三种类型的会议：
1. 预算分配会议（Budget Allocation Conference）
2. 经验分享会议（Experience Sharing Conference）
3. 极端市场会议（Extreme Market Conference）
"""

# 预算分配会议提示
budget_allocation_conference_prompt = """
# 预算分配会议

## 会议目的
在这个会议中，你作为对冲基金经理Otto，需要与分析师团队讨论并决定如何分配投资预算到不同资产类别。

## 会议流程
1. **市场状况评估**：
   - 请每位分析师简要介绍各自负责的市场当前状况
   - 比特币分析师Dave：加密货币市场状况
   - DJ30分析师Bob：股票市场状况
   - 外汇分析师Emily：外汇市场状况

2. **风险评估**：
   - 讨论各个市场的风险水平
   - 确定整体市场风险偏好
   - 识别潜在的系统性风险

3. **表现回顾**：
   - 回顾各资产类别的历史表现
   - 分析哪些策略在当前市场环境中表现最佳
   - 评估之前的预算分配决策效果

4. **预算分配**：
   - 根据市场状况、风险评估和历史表现，决定预算分配比例
   - 考虑以下资产类别：
     * 加密货币（比特币、以太坊等）
     * 股票（个股、指数等）
     * 外汇（主要货币对）
     * 现金储备（风险对冲）

5. **执行计划**：
   - 制定具体的执行计划
   - 设定止损和止盈水平
   - 确定调整预算分配的触发条件

## 输出要求
会议结束后，你需要生成一份预算分配报告，包括：
1. 各资产类别的分配比例
2. 分配决策的理由
3. 风险管理策略
4. 预期收益目标
5. 下次预算审查的时间点
"""

# 经验分享会议提示
experience_sharing_conference_prompt = """
# 经验分享会议

## 会议目的
在这个会议中，你作为对冲基金经理Otto，需要与分析师团队分享和讨论投资经验，以提高团队的整体决策能力。

## 会议流程
1. **成功案例分享**：
   - 请每位分析师分享一个近期成功的投资决策
   - 分析成功的关键因素
   - 讨论如何在未来复制这些成功

2. **失败案例分析**：
   - 请每位分析师分享一个近期失败的投资决策
   - 分析失败的原因
   - 讨论如何避免类似错误

3. **市场洞察**：
   - 分享对当前市场的独特见解
   - 讨论新兴趋势和机会
   - 分析可能被市场忽视的风险

4. **策略讨论**：
   - 讨论新的投资策略和方法
   - 评估现有策略的有效性
   - 探讨如何改进决策流程

5. **知识更新**：
   - 分享最新的研究和行业发展
   - 讨论新技术对市场的影响
   - 更新团队的一般经验记忆

## 输出要求
会议结束后，你需要生成一份经验总结报告，包括：
1. 关键经验教训
2. 可行的改进措施
3. 新的投资见解
4. 更新到团队记忆系统的内容
5. 团队知识库的更新建议
"""

# 极端市场会议提示
extreme_market_conference_prompt = """
# 极端市场会议

## 会议目的
在这个会议中，你作为对冲基金经理Otto，需要与分析师团队紧急讨论如何应对极端市场情况，制定危机应对策略。

## 会议流程
1. **情况评估**：
   - 详细分析当前极端市场情况
   - 评估对各资产类别的影响
   - 确定危机的严重程度和可能持续时间

2. **损失情况**：
   - 评估当前持仓的损失情况
   - 分析损失的原因
   - 确定哪些资产受影响最严重

3. **风险控制**：
   - 讨论如何限制进一步损失
   - 评估是否需要触发止损
   - 考虑对冲策略的有效性

4. **资产处置计划**：
   - 决定是否需要清算某些持仓
   - 制定分阶段减仓或增仓计划
   - 确定优先保护的核心资产

5. **反击策略**：
   - 讨论如何从危机中获利
   - 识别市场过度反应创造的机会
   - 制定逆势投资计划

6. **恢复计划**：
   - 设定市场恢复的指标和信号
   - 制定分阶段重新进入市场的策略
   - 讨论如何重建投资组合

## 输出要求
会议结束后，你需要生成一份危机应对报告，包括：
1. 极端市场情况的简要描述
2. 当前损失评估
3. 即时行动计划
4. 中期调整策略
5. 长期恢复路线图
6. 风险管理改进建议
"""

# 会议系统辅助函数
def get_conference_prompt(conference_type: str) -> str:
    """
    获取指定类型的会议提示
    
    参数:
    - conference_type: 会议类型，可以是"budget_allocation"、"experience_sharing"或"extreme_market"
    
    返回:
    - 会议提示文本
    """
    if conference_type == "budget_allocation":
        return budget_allocation_conference_prompt
    elif conference_type == "experience_sharing":
        return experience_sharing_conference_prompt
    elif conference_type == "extreme_market":
        return extreme_market_conference_prompt
    else:
        return "未知的会议类型。可用的会议类型有：budget_allocation（预算分配会议）、experience_sharing（经验分享会议）和extreme_market（极端市场会议）。"

# 会议结果模板
budget_allocation_result_template = """
# 预算分配会议结果

## 市场状况总结
{market_summary}

## 风险评估
{risk_assessment}

## 预算分配决策
{budget_allocation}

## 执行计划
{execution_plan}

## 下次审查
{next_review}
"""

experience_sharing_result_template = """
# 经验分享会议结果

## 关键经验教训
{key_lessons}

## 改进措施
{improvement_measures}

## 新的投资见解
{new_insights}

## 记忆系统更新
{memory_updates}
"""

extreme_market_result_template = """
# 极端市场会议结果

## 极端情况描述
{extreme_situation}

## 损失评估
{loss_assessment}

## 即时行动计划
{immediate_actions}

## 中期调整策略
{mid_term_strategy}

## 长期恢复路线图
{long_term_recovery}
"""

def get_conference_result_template(conference_type: str) -> str:
    """
    获取指定类型的会议结果模板
    
    参数:
    - conference_type: 会议类型，可以是"budget_allocation"、"experience_sharing"或"extreme_market"
    
    返回:
    - 会议结果模板文本
    """
    if conference_type == "budget_allocation":
        return budget_allocation_result_template
    elif conference_type == "experience_sharing":
        return experience_sharing_result_template
    elif conference_type == "extreme_market":
        return extreme_market_result_template
    else:
        return "未知的会议类型。"
