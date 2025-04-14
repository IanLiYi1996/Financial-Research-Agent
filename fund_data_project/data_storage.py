#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据存储模块，提供CSV和SQLite存储功能
"""
import os
import pandas as pd
from sqlalchemy import create_engine

def save_to_csv(df, file_path):
    """
    将DataFrame保存为CSV文件
    
    参数:
        df (pandas.DataFrame): 要保存的数据
        file_path (str): CSV文件路径
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 保存为CSV，使用UTF-8编码
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"数据已保存到: {file_path}")

def save_to_sqlite(df, db_name, table_name, if_exists='replace'):
    """
    将DataFrame保存到SQLite数据库
    
    参数:
        df (pandas.DataFrame): 要保存的数据
        db_name (str): 数据库文件名
        table_name (str): 表名
        if_exists (str): 如果表已存在的处理方式，可选值: 'fail', 'replace', 'append'
    """
    # 创建SQLite连接
    engine = create_engine(f'sqlite:///{db_name}')
    
    # 保存到数据库
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    print(f"数据已保存到数据库: {db_name}, 表: {table_name}")

def read_from_csv(file_path):
    """
    从CSV文件读取数据
    
    参数:
        file_path (str): CSV文件路径
        
    返回:
        pandas.DataFrame: 读取的数据
    """
    return pd.read_csv(file_path, encoding='utf-8-sig')

def read_from_sqlite(db_name, table_name):
    """
    从SQLite数据库读取数据
    
    参数:
        db_name (str): 数据库文件名
        table_name (str): 表名
        
    返回:
        pandas.DataFrame: 读取的数据
    """
    engine = create_engine(f'sqlite:///{db_name}')
    return pd.read_sql_table(table_name, engine)
