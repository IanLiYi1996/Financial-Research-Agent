#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基金数据爬取模块，使用AKShare库获取各类基金数据
支持增量更新和断点续传功能
"""
import time
import random
import os
import json
import pandas as pd
from tqdm import tqdm
import akshare as ak
from data_storage import save_to_csv, save_to_sqlite, read_from_csv, read_from_sqlite

# 定义进度文件和临时数据目录
PROGRESS_DIR = "./progress"
TEMP_DATA_DIR = "./temp_data"

# 确保目录存在
os.makedirs(PROGRESS_DIR, exist_ok=True)
os.makedirs(TEMP_DATA_DIR, exist_ok=True)

def save_progress(task_name, processed_codes, total_codes=None):
    """
    保存处理进度
    
    参数:
        task_name (str): 任务名称，如'nav', 'position'等
        processed_codes (list): 已处理的基金代码列表
        total_codes (list): 总的基金代码列表，默认为None
    """
    progress_file = os.path.join(PROGRESS_DIR, f"{task_name}_progress.json")
    
    progress_data = {
        'processed_codes': processed_codes,
        'last_update': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if total_codes:
        progress_data['total_codes'] = total_codes
        progress_data['remaining_codes'] = [code for code in total_codes if code not in processed_codes]
        progress_data['completion_percentage'] = len(processed_codes) / len(total_codes) * 100 if total_codes else 0
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)
    
    print(f"进度已保存到: {progress_file}")

def load_progress(task_name):
    """
    加载处理进度
    
    参数:
        task_name (str): 任务名称，如'nav', 'position'等
        
    返回:
        dict: 进度数据，如果文件不存在则返回空字典
    """
    progress_file = os.path.join(PROGRESS_DIR, f"{task_name}_progress.json")
    
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            print(f"已加载进度文件: {progress_file}")
            return progress_data
        except Exception as e:
            print(f"加载进度文件失败: {e}")
            return {}
    else:
        print(f"进度文件不存在: {progress_file}")
        return {}

def get_remaining_codes(task_name, all_codes):
    """
    获取剩余未处理的基金代码
    
    参数:
        task_name (str): 任务名称，如'nav', 'position'等
        all_codes (list): 所有基金代码列表
        
    返回:
        list: 剩余未处理的基金代码列表
    """
    progress_data = load_progress(task_name)
    
    if progress_data and 'processed_codes' in progress_data:
        processed_codes = set(progress_data['processed_codes'])
        remaining_codes = [code for code in all_codes if code not in processed_codes]
        print(f"任务 {task_name} 已处理 {len(processed_codes)} 只基金，剩余 {len(remaining_codes)} 只基金")
        return remaining_codes
    else:
        print(f"任务 {task_name} 没有进度记录，将处理所有 {len(all_codes)} 只基金")
        return all_codes

def save_temp_data(task_name, fund_code, data_df):
    """
    保存单个基金的临时数据
    
    参数:
        task_name (str): 任务名称，如'nav', 'position'等
        fund_code (str): 基金代码
        data_df (pandas.DataFrame): 基金数据
    """
    if data_df.empty:
        return
        
    temp_file = os.path.join(TEMP_DATA_DIR, f"{task_name}_{fund_code}.csv")
    data_df.to_csv(temp_file, index=False, encoding='utf-8-sig')

def merge_temp_data(task_name, output_file=None, db_name=None, table_name=None):
    """
    合并临时数据文件
    
    参数:
        task_name (str): 任务名称，如'nav', 'position'等
        output_file (str): 输出CSV文件路径，默认为None
        db_name (str): 数据库文件名，默认为None
        table_name (str): 表名，默认为None
    
    返回:
        pandas.DataFrame: 合并后的数据
    """
    temp_files = [f for f in os.listdir(TEMP_DATA_DIR) if f.startswith(f"{task_name}_") and f.endswith(".csv")]
    
    if not temp_files:
        print(f"没有找到任务 {task_name} 的临时数据文件")
        return pd.DataFrame()
    
    all_data = pd.DataFrame()
    
    for temp_file in temp_files:
        file_path = os.path.join(TEMP_DATA_DIR, temp_file)
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            all_data = pd.concat([all_data, df], ignore_index=True)
        except Exception as e:
            print(f"读取临时文件 {temp_file} 失败: {e}")
    
    # 保存合并后的数据
    if output_file:
        save_to_csv(all_data, output_file)
    
    if db_name and table_name:
        save_to_sqlite(all_data, db_name, table_name)
    
    return all_data

def clean_temp_data(task_name=None):
    """
    清理临时数据文件
    
    参数:
        task_name (str): 任务名称，如'nav', 'position'等，默认为None表示清理所有临时文件
    """
    if task_name:
        temp_files = [f for f in os.listdir(TEMP_DATA_DIR) if f.startswith(f"{task_name}_") and f.endswith(".csv")]
    else:
        temp_files = [f for f in os.listdir(TEMP_DATA_DIR) if f.endswith(".csv")]
    
    for temp_file in temp_files:
        file_path = os.path.join(TEMP_DATA_DIR, temp_file)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"删除临时文件 {temp_file} 失败: {e}")
    
    print(f"已清理 {len(temp_files)} 个临时文件")

def get_fund_basic_info():
    """
    获取所有基金的基本信息数据
    
    返回:
        pandas.DataFrame: 基金基本信息数据
    """
    print("正在获取基金基本信息...")
    try:
        # 使用AKShare获取基金基本信息
        fund_info_df = ak.fund_name_em()
        print(f"成功获取 {len(fund_info_df)} 只基金的基本信息")
        return fund_info_df
    except Exception as e:
        print(f"获取基金基本信息失败: {e}")
        return pd.DataFrame()

def get_fund_nav_info(fund_codes=None, start_date="20000101", end_date=None, output_file=None, db_name=None, table_name=None, incremental=True):
    """
    获取基金净值信息，支持增量更新和断点续传
    
    参数:
        fund_codes (list): 基金代码列表，默认为None表示获取所有基金
        start_date (str): 开始日期，格式为YYYYMMDD
        end_date (str): 结束日期，格式为YYYYMMDD，默认为None表示当前日期
        output_file (str): 输出CSV文件路径，默认为None
        db_name (str): 数据库文件名，默认为None
        table_name (str): 表名，默认为None
        incremental (bool): 是否增量更新，默认为True
    
    返回:
        pandas.DataFrame: 基金净值信息数据
    """
    task_name = "nav"
    
    if fund_codes is None:
        # 如果未指定基金代码，则获取所有基金代码
        try:
            fund_info_df = ak.fund_name_em()
            fund_codes = fund_info_df['基金代码'].tolist()
            print(f"将获取 {len(fund_codes)} 只基金的净值信息")
        except Exception as e:
            print(f"获取基金代码列表失败: {e}")
            return pd.DataFrame()
    
    # 如果是增量更新，获取剩余未处理的基金代码
    if incremental:
        fund_codes = get_remaining_codes(task_name, fund_codes)
    
    # 如果没有需要处理的基金代码，直接返回已有数据
    if not fund_codes:
        print("没有需要处理的基金代码，将合并已有数据")
        return merge_temp_data(task_name, output_file, db_name, table_name)
    
    # 记录已处理的基金代码
    processed_codes = []
    
    # 加载已有的进度
    progress_data = load_progress(task_name)
    if progress_data and 'processed_codes' in progress_data:
        processed_codes = progress_data['processed_codes']
    
    # 使用tqdm显示进度条
    for fund_code in tqdm(fund_codes, desc="获取基金净值信息"):
        try:
            # 场外基金净值信息
            if len(fund_code) == 6:
                # 开放式基金历史净值
                fund_nav_df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
                fund_nav_df['基金代码'] = fund_code
                
                # 保存单个基金的数据
                save_temp_data(task_name, fund_code, fund_nav_df)
            
            # 场内基金净值信息
            elif len(fund_code) == 6 and fund_code.startswith(('5', '1')):
                # ETF基金历史净值
                fund_nav_df = ak.fund_etf_hist_em(symbol=fund_code, period="daily", 
                                                 start_date=start_date, end_date=end_date)
                fund_nav_df['基金代码'] = fund_code
                
                # 保存单个基金的数据
                save_temp_data(task_name, fund_code, fund_nav_df)
            
            # 记录已处理的基金代码
            processed_codes.append(fund_code)
            
            # 每处理10个基金保存一次进度
            if len(processed_codes) % 10 == 0:
                save_progress(task_name, processed_codes, fund_codes)
            
            # 随机暂停一下，避免请求过于频繁
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"获取基金 {fund_code} 净值信息失败: {e}")
            continue
    
    # 保存最终进度
    save_progress(task_name, processed_codes, fund_codes)
    
    # 合并所有临时数据
    all_nav_df = merge_temp_data(task_name, output_file, db_name, table_name)
    
    return all_nav_df

def get_fund_position_info(fund_codes=None, year="2023", output_file=None, db_name=None, table_name=None, incremental=True):
    """
    获取基金持仓信息，支持增量更新和断点续传
    
    参数:
        fund_codes (list): 基金代码列表，默认为None表示获取所有基金
        year (str): 年份，默认为"2023"
        output_file (str): 输出CSV文件路径，默认为None
        db_name (str): 数据库文件名，默认为None
        table_name (str): 表名，默认为None
        incremental (bool): 是否增量更新，默认为True
    
    返回:
        pandas.DataFrame: 基金持仓信息数据
    """
    task_name = "position"
    
    if fund_codes is None:
        # 如果未指定基金代码，则获取所有基金代码
        try:
            fund_info_df = ak.fund_name_em()
            fund_codes = fund_info_df['基金代码'].tolist()
            print(f"将获取 {len(fund_codes)} 只基金的持仓信息")
        except Exception as e:
            print(f"获取基金代码列表失败: {e}")
            return pd.DataFrame()
    
    # 如果是增量更新，获取剩余未处理的基金代码
    if incremental:
        fund_codes = get_remaining_codes(task_name, fund_codes)
    
    # 如果没有需要处理的基金代码，直接返回已有数据
    if not fund_codes:
        print("没有需要处理的基金代码，将合并已有数据")
        return merge_temp_data(task_name, output_file, db_name, table_name)
    
    # 记录已处理的基金代码
    processed_codes = []
    
    # 加载已有的进度
    progress_data = load_progress(task_name)
    if progress_data and 'processed_codes' in progress_data:
        processed_codes = progress_data['processed_codes']
    
    # 使用tqdm显示进度条
    for fund_code in tqdm(fund_codes, desc="获取基金持仓信息"):
        try:
            # 获取股票持仓
            try:
                stock_df = ak.fund_portfolio_hold_em(symbol=fund_code, date=year)
                if not stock_df.empty:
                    stock_df['基金代码'] = fund_code
                    stock_df['持仓类型'] = '股票'
                    # 保存单个基金的股票持仓数据
                    save_temp_data(f"{task_name}_stock", fund_code, stock_df)
            except Exception as e:
                print(f"获取基金 {fund_code} 股票持仓失败: {e}")
            
            # 获取债券持仓
            try:
                bond_df = ak.fund_portfolio_bond_hold_em(symbol=fund_code, date=year)
                if not bond_df.empty:
                    bond_df['基金代码'] = fund_code
                    bond_df['持仓类型'] = '债券'
                    # 保存单个基金的债券持仓数据
                    save_temp_data(f"{task_name}_bond", fund_code, bond_df)
            except Exception as e:
                print(f"获取基金 {fund_code} 债券持仓失败: {e}")
            
            # 记录已处理的基金代码
            processed_codes.append(fund_code)
            
            # 每处理10个基金保存一次进度
            if len(processed_codes) % 10 == 0:
                save_progress(task_name, processed_codes, fund_codes)
            
            # 随机暂停一下，避免请求过于频繁
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"获取基金 {fund_code} 持仓信息失败: {e}")
            continue
    
    # 保存最终进度
    save_progress(task_name, processed_codes, fund_codes)
    
    # 合并所有临时数据
    stock_position_df = merge_temp_data(f"{task_name}_stock")
    bond_position_df = merge_temp_data(f"{task_name}_bond")
    
    # 合并股票持仓和债券持仓
    position_df = pd.DataFrame()
    if not stock_position_df.empty:
        position_df = pd.concat([position_df, stock_position_df], ignore_index=True)
    
    if not bond_position_df.empty:
        position_df = pd.concat([position_df, bond_position_df], ignore_index=True)
    
    # 保存合并后的数据
    if output_file and not position_df.empty:
        save_to_csv(position_df, output_file)
    
    if db_name and table_name and not position_df.empty:
        save_to_sqlite(position_df, db_name, table_name)
    
    return position_df

def get_fund_manager_info(output_file=None, db_name=None, table_name=None):
    """
    获取基金经理信息，支持保存到文件或数据库
    
    参数:
        output_file (str): 输出CSV文件路径，默认为None
        db_name (str): 数据库文件名，默认为None
        table_name (str): 表名，默认为None
    
    返回:
        pandas.DataFrame: 基金经理信息数据
    """
    task_name = "manager"
    print("正在获取基金经理信息...")
    
    # 检查是否有临时保存的数据
    temp_file = os.path.join(TEMP_DATA_DIR, f"{task_name}_data.csv")
    if os.path.exists(temp_file):
        try:
            manager_df = pd.read_csv(temp_file, encoding='utf-8-sig')
            print(f"从临时文件加载了 {len(manager_df)} 条基金经理信息")
            
            # 保存到指定位置
            if output_file:
                save_to_csv(manager_df, output_file)
            
            if db_name and table_name:
                save_to_sqlite(manager_df, db_name, table_name)
                
            return manager_df
        except Exception as e:
            print(f"读取临时文件失败: {e}")
    
    try:
        # 使用AKShare获取基金经理信息
        manager_df = ak.fund_manager_em()
        print(f"成功获取 {len(manager_df)} 条基金经理信息")
        
        # 保存临时文件
        if not manager_df.empty:
            manager_df.to_csv(temp_file, index=False, encoding='utf-8-sig')
            print(f"基金经理信息已保存到临时文件: {temp_file}")
        
        # 保存到指定位置
        if output_file:
            save_to_csv(manager_df, output_file)
        
        if db_name and table_name:
            save_to_sqlite(manager_df, db_name, table_name)
            
        return manager_df
    except Exception as e:
        print(f"获取基金经理信息失败: {e}")
        return pd.DataFrame()

def get_fund_performance_info(output_file=None, db_name=None, table_name=None):
    """
    获取基金业绩信息，支持保存到文件或数据库
    
    参数:
        output_file (str): 输出CSV文件路径，默认为None
        db_name (str): 数据库文件名，默认为None
        table_name (str): 表名，默认为None
    
    返回:
        pandas.DataFrame: 基金业绩信息数据
    """
    task_name = "performance"
    print("正在获取基金业绩信息...")
    
    # 检查是否有临时保存的数据
    temp_file = os.path.join(TEMP_DATA_DIR, f"{task_name}_data.csv")
    if os.path.exists(temp_file):
        try:
            performance_df = pd.read_csv(temp_file, encoding='utf-8-sig')
            print(f"从临时文件加载了 {len(performance_df)} 条基金业绩信息")
            
            # 保存到指定位置
            if output_file:
                save_to_csv(performance_df, output_file)
            
            if db_name and table_name:
                save_to_sqlite(performance_df, db_name, table_name)
                
            return performance_df
        except Exception as e:
            print(f"读取临时文件失败: {e}")
    
    try:
        # 使用AKShare获取开放式基金排行
        performance_df = ak.fund_open_fund_rank_em(symbol="全部")
        print(f"成功获取 {len(performance_df)} 只基金的业绩信息")
        
        # 保存临时文件
        if not performance_df.empty:
            performance_df.to_csv(temp_file, index=False, encoding='utf-8-sig')
            print(f"基金业绩信息已保存到临时文件: {temp_file}")
        
        # 保存到指定位置
        if output_file:
            save_to_csv(performance_df, output_file)
        
        if db_name and table_name:
            save_to_sqlite(performance_df, db_name, table_name)
            
        return performance_df
    except Exception as e:
        print(f"获取基金业绩信息失败: {e}")
        return pd.DataFrame()

def get_fund_industry_allocation(fund_codes=None, year="2023", output_file=None, db_name=None, table_name=None, incremental=True):
    """
    获取基金行业配置信息，支持增量更新和断点续传
    
    参数:
        fund_codes (list): 基金代码列表，默认为None表示获取所有基金
        year (str): 年份，默认为"2023"
        output_file (str): 输出CSV文件路径，默认为None
        db_name (str): 数据库文件名，默认为None
        table_name (str): 表名，默认为None
        incremental (bool): 是否增量更新，默认为True
    
    返回:
        pandas.DataFrame: 基金行业配置信息数据
    """
    task_name = "industry"
    
    if fund_codes is None:
        # 如果未指定基金代码，则获取所有基金代码
        try:
            fund_info_df = ak.fund_name_em()
            fund_codes = fund_info_df['基金代码'].tolist()
            print(f"将获取 {len(fund_codes)} 只基金的行业配置信息")
        except Exception as e:
            print(f"获取基金代码列表失败: {e}")
            return pd.DataFrame()
    
    # 如果是增量更新，获取剩余未处理的基金代码
    if incremental:
        fund_codes = get_remaining_codes(task_name, fund_codes)
    
    # 如果没有需要处理的基金代码，直接返回已有数据
    if not fund_codes:
        print("没有需要处理的基金代码，将合并已有数据")
        return merge_temp_data(task_name, output_file, db_name, table_name)
    
    # 记录已处理的基金代码
    processed_codes = []
    
    # 加载已有的进度
    progress_data = load_progress(task_name)
    if progress_data and 'processed_codes' in progress_data:
        processed_codes = progress_data['processed_codes']
    
    # 使用tqdm显示进度条
    for fund_code in tqdm(fund_codes, desc="获取基金行业配置信息"):
        try:
            # 获取行业配置
            industry_df = ak.fund_portfolio_industry_allocation_em(symbol=fund_code, date=year)
            if not industry_df.empty:
                industry_df['基金代码'] = fund_code
                # 保存单个基金的行业配置数据
                save_temp_data(task_name, fund_code, industry_df)
            
            # 记录已处理的基金代码
            processed_codes.append(fund_code)
            
            # 每处理10个基金保存一次进度
            if len(processed_codes) % 10 == 0:
                save_progress(task_name, processed_codes, fund_codes)
            
            # 随机暂停一下，避免请求过于频繁
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"获取基金 {fund_code} 行业配置信息失败: {e}")
            continue
    
    # 保存最终进度
    save_progress(task_name, processed_codes, fund_codes)
    
    # 合并所有临时数据
    industry_allocation_df = merge_temp_data(task_name, output_file, db_name, table_name)
    
    return industry_allocation_df
