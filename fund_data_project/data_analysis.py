#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基金数据分析模块，提供基金数据分析和可视化功能
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from data_storage import read_from_csv, read_from_sqlite

# 设置中文字体，解决中文显示问题
try:
    # 尝试设置微软雅黑字体
    font = FontProperties(fname=r"C:\Windows\Fonts\msyh.ttc")
except:
    try:
        # 尝试设置苹果系统中文字体
        font = FontProperties(fname=r"/System/Library/Fonts/PingFang.ttc")
    except:
        # 使用系统默认字体
        font = FontProperties()

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Heiti SC', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def analyze_fund_performance(data_source, output_dir='./analysis_results'):
    """
    分析基金业绩表现
    
    参数:
        data_source (str): 数据源，可以是CSV文件路径或SQLite数据库名称
        output_dir (str): 分析结果输出目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取基金业绩数据
    if data_source.endswith('.csv'):
        performance_df = read_from_csv(data_source)
    else:
        performance_df = read_from_sqlite(data_source, 'fund_performance_info')
    
    # 确保数据不为空
    if performance_df.empty:
        print("基金业绩数据为空，无法进行分析")
        return
    
    # 分析近1年收益率分布
    plt.figure(figsize=(12, 8))
    plt.hist(performance_df['近1年'], bins=50, alpha=0.7, color='blue')
    plt.title('基金近1年收益率分布', fontproperties=font, fontsize=16)
    plt.xlabel('收益率(%)', fontproperties=font, fontsize=14)
    plt.ylabel('基金数量', fontproperties=font, fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(output_dir, '基金近1年收益率分布.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 分析不同类型基金的平均收益率
    if '基金类型' in performance_df.columns:
        type_performance = performance_df.groupby('基金类型')['近1年', '近3年', '近5年'].mean().sort_values('近1年', ascending=False)
        
        # 绘制不同类型基金的平均收益率柱状图
        plt.figure(figsize=(14, 10))
        type_performance['近1年'].plot(kind='bar', color='blue', alpha=0.7)
        plt.title('不同类型基金近1年平均收益率', fontproperties=font, fontsize=16)
        plt.xlabel('基金类型', fontproperties=font, fontsize=14)
        plt.ylabel('平均收益率(%)', fontproperties=font, fontsize=14)
        plt.xticks(rotation=45, ha='right', fontproperties=font)
        plt.grid(True, linestyle='--', alpha=0.7, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '不同类型基金近1年平均收益率.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    # 输出业绩排名前20的基金
    top_funds = performance_df.sort_values('近1年', ascending=False).head(20)
    top_funds.to_csv(os.path.join(output_dir, '业绩排名前20基金.csv'), index=False, encoding='utf-8-sig')
    
    print(f"基金业绩分析完成，结果已保存到 {output_dir} 目录")

def analyze_fund_holdings(data_source, output_dir='./analysis_results'):
    """
    分析基金持仓情况
    
    参数:
        data_source (str): 数据源，可以是CSV文件路径或SQLite数据库名称
        output_dir (str): 分析结果输出目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取基金持仓数据
    if data_source.endswith('.csv'):
        holdings_df = read_from_csv(data_source)
    else:
        holdings_df = read_from_sqlite(data_source, 'fund_position_info')
    
    # 确保数据不为空
    if holdings_df.empty:
        print("基金持仓数据为空，无法进行分析")
        return
    
    # 分析股票持仓
    if '持仓类型' in holdings_df.columns and '股票名称' in holdings_df.columns:
        stock_holdings = holdings_df[holdings_df['持仓类型'] == '股票']
        
        # 统计出现频率最高的股票（最受基金青睐的股票）
        top_stocks = stock_holdings['股票名称'].value_counts().head(20)
        
        # 绘制最受基金青睐的股票柱状图
        plt.figure(figsize=(14, 10))
        top_stocks.plot(kind='bar', color='red', alpha=0.7)
        plt.title('最受基金青睐的前20只股票', fontproperties=font, fontsize=16)
        plt.xlabel('股票名称', fontproperties=font, fontsize=14)
        plt.ylabel('持有基金数量', fontproperties=font, fontsize=14)
        plt.xticks(rotation=45, ha='right', fontproperties=font)
        plt.grid(True, linestyle='--', alpha=0.7, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '最受基金青睐的前20只股票.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 保存最受基金青睐的股票数据
        top_stocks_df = pd.DataFrame({'股票名称': top_stocks.index, '持有基金数量': top_stocks.values})
        top_stocks_df.to_csv(os.path.join(output_dir, '最受基金青睐的前20只股票.csv'), index=False, encoding='utf-8-sig')
    
    # 分析债券持仓
    if '持仓类型' in holdings_df.columns and '债券名称' in holdings_df.columns:
        bond_holdings = holdings_df[holdings_df['持仓类型'] == '债券']
        
        # 统计出现频率最高的债券
        top_bonds = bond_holdings['债券名称'].value_counts().head(20)
        
        # 绘制最受基金青睐的债券柱状图
        plt.figure(figsize=(14, 10))
        top_bonds.plot(kind='bar', color='green', alpha=0.7)
        plt.title('最受基金青睐的前20只债券', fontproperties=font, fontsize=16)
        plt.xlabel('债券名称', fontproperties=font, fontsize=14)
        plt.ylabel('持有基金数量', fontproperties=font, fontsize=14)
        plt.xticks(rotation=45, ha='right', fontproperties=font)
        plt.grid(True, linestyle='--', alpha=0.7, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '最受基金青睐的前20只债券.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 保存最受基金青睐的债券数据
        top_bonds_df = pd.DataFrame({'债券名称': top_bonds.index, '持有基金数量': top_bonds.values})
        top_bonds_df.to_csv(os.path.join(output_dir, '最受基金青睐的前20只债券.csv'), index=False, encoding='utf-8-sig')
    
    print(f"基金持仓分析完成，结果已保存到 {output_dir} 目录")

def analyze_fund_managers(data_source, output_dir='./analysis_results'):
    """
    分析基金经理情况
    
    参数:
        data_source (str): 数据源，可以是CSV文件路径或SQLite数据库名称
        output_dir (str): 分析结果输出目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取基金经理数据
    if data_source.endswith('.csv'):
        managers_df = read_from_csv(data_source)
    else:
        managers_df = read_from_sqlite(data_source, 'fund_manager_info')
    
    # 确保数据不为空
    if managers_df.empty:
        print("基金经理数据为空，无法进行分析")
        return
    
    # 分析基金经理管理基金数量分布
    if '姓名' in managers_df.columns:
        manager_fund_counts = managers_df['姓名'].value_counts()
        
        plt.figure(figsize=(12, 8))
        plt.hist(manager_fund_counts.values, bins=30, alpha=0.7, color='purple')
        plt.title('基金经理管理基金数量分布', fontproperties=font, fontsize=16)
        plt.xlabel('管理基金数量', fontproperties=font, fontsize=14)
        plt.ylabel('基金经理数量', fontproperties=font, fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(os.path.join(output_dir, '基金经理管理基金数量分布.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 管理基金数量最多的前20名基金经理
        top_managers = manager_fund_counts.head(20)
        
        plt.figure(figsize=(14, 10))
        top_managers.plot(kind='bar', color='orange', alpha=0.7)
        plt.title('管理基金数量最多的前20名基金经理', fontproperties=font, fontsize=16)
        plt.xlabel('基金经理', fontproperties=font, fontsize=14)
        plt.ylabel('管理基金数量', fontproperties=font, fontsize=14)
        plt.xticks(rotation=45, ha='right', fontproperties=font)
        plt.grid(True, linestyle='--', alpha=0.7, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, '管理基金数量最多的前20名基金经理.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 保存管理基金数量最多的基金经理数据
        top_managers_df = pd.DataFrame({'基金经理': top_managers.index, '管理基金数量': top_managers.values})
        top_managers_df.to_csv(os.path.join(output_dir, '管理基金数量最多的前20名基金经理.csv'), index=False, encoding='utf-8-sig')
    
    # 分析基金经理的平均任职时间
    if '累计从业时间' in managers_df.columns:
        plt.figure(figsize=(12, 8))
        plt.hist(managers_df['累计从业时间'].values, bins=30, alpha=0.7, color='brown')
        plt.title('基金经理累计从业时间分布', fontproperties=font, fontsize=16)
        plt.xlabel('累计从业时间(天)', fontproperties=font, fontsize=14)
        plt.ylabel('基金经理数量', fontproperties=font, fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(os.path.join(output_dir, '基金经理累计从业时间分布.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"基金经理分析完成，结果已保存到 {output_dir} 目录")

def analyze_fund_nav_trend(data_source, fund_codes=None, output_dir='./analysis_results'):
    """
    分析基金净值走势
    
    参数:
        data_source (str): 数据源，可以是CSV文件路径或SQLite数据库名称
        fund_codes (list): 要分析的基金代码列表，默认为None表示随机选择10只基金
        output_dir (str): 分析结果输出目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取基金净值数据
    if data_source.endswith('.csv'):
        nav_df = read_from_csv(data_source)
    else:
        nav_df = read_from_sqlite(data_source, 'fund_nav_info')
    
    # 确保数据不为空
    if nav_df.empty:
        print("基金净值数据为空，无法进行分析")
        return
    
    # 如果未指定基金代码，则随机选择10只基金
    if fund_codes is None:
        all_fund_codes = nav_df['基金代码'].unique()
        if len(all_fund_codes) > 10:
            fund_codes = np.random.choice(all_fund_codes, 10, replace=False)
        else:
            fund_codes = all_fund_codes
    
    # 分析每只基金的净值走势
    for fund_code in fund_codes:
        fund_nav = nav_df[nav_df['基金代码'] == fund_code].copy()
        
        # 确保有足够的数据
        if len(fund_nav) < 10:
            print(f"基金 {fund_code} 的净值数据不足，跳过分析")
            continue
        
        # 确保日期列是日期类型
        if '净值日期' in fund_nav.columns:
            fund_nav['净值日期'] = pd.to_datetime(fund_nav['净值日期'])
            fund_nav = fund_nav.sort_values('净值日期')
            
            # 绘制净值走势图
            plt.figure(figsize=(14, 8))
            
            if '单位净值' in fund_nav.columns:
                plt.plot(fund_nav['净值日期'], fund_nav['单位净值'], label='单位净值', color='blue', linewidth=2)
            
            if '累计净值' in fund_nav.columns and not fund_nav['累计净值'].isna().all():
                plt.plot(fund_nav['净值日期'], fund_nav['累计净值'], label='累计净值', color='red', linewidth=2, linestyle='--')
            
            plt.title(f'基金 {fund_code} 净值走势', fontproperties=font, fontsize=16)
            plt.xlabel('日期', fontproperties=font, fontsize=14)
            plt.ylabel('净值', fontproperties=font, fontsize=14)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend(prop=font)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'基金{fund_code}净值走势.png'), dpi=300, bbox_inches='tight')
            plt.close()
    
    print(f"基金净值走势分析完成，结果已保存到 {output_dir} 目录")

if __name__ == "__main__":
    # 示例用法
    analyze_fund_performance('./data/fund_performance_info.csv')
    analyze_fund_holdings('./data/fund_position_info.csv')
    analyze_fund_managers('./data/fund_manager_info.csv')
    analyze_fund_nav_trend('./data/fund_nav_info.csv')
