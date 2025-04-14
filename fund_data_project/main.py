#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
公募基金数据获取与存储主程序
支持增量更新和断点续传功能
"""
import os
import argparse
from datetime import datetime
import pandas as pd
from fund_crawler import (
    get_fund_basic_info,
    get_fund_nav_info,
    get_fund_position_info,
    get_fund_manager_info,
    get_fund_performance_info,
    get_fund_industry_allocation,
    clean_temp_data
)
from data_storage import save_to_csv, save_to_sqlite

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='公募基金数据获取与存储工具')
    parser.add_argument('--output', type=str, default='csv', choices=['csv', 'sqlite'],
                        help='数据存储格式: csv或sqlite (默认: csv)')
    parser.add_argument('--data-dir', type=str, default='./data',
                        help='数据存储目录 (默认: ./data)')
    parser.add_argument('--db-name', type=str, default='fund_data.db',
                        help='SQLite数据库名称 (默认: fund_data.db)')
    parser.add_argument('--modules', type=str, nargs='+',
                        default=['basic', 'nav', 'position', 'manager', 'performance', 'industry'],
                        help='要获取的数据模块 (默认: 全部)')
    parser.add_argument('--incremental', action='store_true',
                        help='启用增量更新模式，只获取未处理的基金数据')
    parser.add_argument('--no-incremental', dest='incremental', action='store_false',
                        help='禁用增量更新模式，获取所有基金数据')
    parser.add_argument('--clean-temp', action='store_true',
                        help='清理临时数据文件')
    parser.add_argument('--year', type=str, default=str(datetime.now().year),
                        help='获取指定年份的持仓和行业配置数据 (默认: 当前年份)')
    parser.add_argument('--start-date', type=str, default="20000101",
                        help='净值数据开始日期，格式为YYYYMMDD (默认: 20000101)')
    parser.add_argument('--end-date', type=str, default=None,
                        help='净值数据结束日期，格式为YYYYMMDD (默认: 当前日期)')
    parser.set_defaults(incremental=True)
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 确保数据目录存在
    os.makedirs(args.data_dir, exist_ok=True)
    
    # 如果需要清理临时数据
    if args.clean_temp:
        print("清理临时数据文件...")
        clean_temp_data()
    
    print(f"开始获取公募基金数据，存储格式: {args.output}, 增量更新模式: {args.incremental}")
    start_time = datetime.now()
    
    # 获取并存储基金基本信息
    if 'basic' in args.modules:
        print("\n获取基金基本信息...")
        basic_info_df = get_fund_basic_info()
        if not basic_info_df.empty:
            output_file = os.path.join(args.data_dir, 'fund_basic_info.csv') if args.output == 'csv' else None
            if args.output == 'csv':
                save_to_csv(basic_info_df, output_file)
            else:
                save_to_sqlite(basic_info_df, args.db_name, 'fund_basic_info')
            print(f"基金基本信息获取完成，共 {len(basic_info_df)} 条记录")
        else:
            print("未获取到基金基本信息数据")
    
    # 获取并存储基金净值信息
    if 'nav' in args.modules:
        print("\n获取基金净值信息...")
        output_file = os.path.join(args.data_dir, 'fund_nav_info.csv') if args.output == 'csv' else None
        nav_info_df = get_fund_nav_info(
            start_date=args.start_date,
            end_date=args.end_date,
            output_file=output_file,
            db_name=args.db_name if args.output == 'sqlite' else None,
            table_name='fund_nav_info' if args.output == 'sqlite' else None,
            incremental=args.incremental
        )
        print(f"基金净值信息获取完成，共 {len(nav_info_df)} 条记录")
    
    # 获取并存储基金持仓信息
    if 'position' in args.modules:
        print("\n获取基金持仓信息...")
        output_file = os.path.join(args.data_dir, 'fund_position_info.csv') if args.output == 'csv' else None
        position_info_df = get_fund_position_info(
            year=args.year,
            output_file=output_file,
            db_name=args.db_name if args.output == 'sqlite' else None,
            table_name='fund_position_info' if args.output == 'sqlite' else None,
            incremental=args.incremental
        )
        print(f"基金持仓信息获取完成，共 {len(position_info_df)} 条记录")
    
    # 获取并存储基金行业配置信息
    if 'industry' in args.modules:
        print("\n获取基金行业配置信息...")
        output_file = os.path.join(args.data_dir, 'fund_industry_allocation.csv') if args.output == 'csv' else None
        industry_info_df = get_fund_industry_allocation(
            year=args.year,
            output_file=output_file,
            db_name=args.db_name if args.output == 'sqlite' else None,
            table_name='fund_industry_allocation' if args.output == 'sqlite' else None,
            incremental=args.incremental
        )
        print(f"基金行业配置信息获取完成，共 {len(industry_info_df)} 条记录")
    
    # 获取并存储基金经理信息
    if 'manager' in args.modules:
        print("\n获取基金经理信息...")
        output_file = os.path.join(args.data_dir, 'fund_manager_info.csv') if args.output == 'csv' else None
        manager_info_df = get_fund_manager_info(
            output_file=output_file,
            db_name=args.db_name if args.output == 'sqlite' else None,
            table_name='fund_manager_info' if args.output == 'sqlite' else None
        )
        print(f"基金经理信息获取完成，共 {len(manager_info_df)} 条记录")
    
    # 获取并存储基金业绩信息
    if 'performance' in args.modules:
        print("\n获取基金业绩信息...")
        output_file = os.path.join(args.data_dir, 'fund_performance_info.csv') if args.output == 'csv' else None
        performance_info_df = get_fund_performance_info(
            output_file=output_file,
            db_name=args.db_name if args.output == 'sqlite' else None,
            table_name='fund_performance_info' if args.output == 'sqlite' else None
        )
        print(f"基金业绩信息获取完成，共 {len(performance_info_df)} 条记录")
    
    end_time = datetime.now()
    print(f"\n数据获取完成，总耗时: {end_time - start_time}")

if __name__ == "__main__":
    main()
