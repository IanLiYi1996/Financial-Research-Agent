#!/usr/bin/env python3
import sys
import json
import boto3
import os
import importlib.util
import traceback
from pathlib import Path

# 加载配置
with open('config.local.json', 'r') as f:
    config = json.load(f)

# 设置AWS区域
os.environ['AWS_REGION'] = config['aws']['region']

# 导入共享模块
sys.path.append(str(Path('./lambdas/layer/python')))
try:
    from models import FinancialReportData, VerificationResult
except ImportError:
    print(json.dumps({"error": "无法导入共享模块，请确保已安装依赖"}))
    sys.exit(1)

# 动态导入Lambda处理程序
def import_handler(module_path):
    try:
        spec = importlib.util.spec_from_file_location("module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.lambda_handler
    except Exception as e:
        print(json.dumps({"error": f"导入处理程序失败: {str(e)}"}))
        sys.exit(1)

# 导入各个Lambda处理程序
planning_handler = import_handler('./lambdas/planning/handler.py')
search_handler = import_handler('./lambdas/search/handler.py')
analysis_handler = import_handler('./lambdas/analysis/handler.py')
report_handler = import_handler('./lambdas/report/handler.py')
verification_handler = import_handler('./lambdas/verification/handler.py')

def main():
    # 获取查询
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    if not query:
        print(json.dumps({"error": "缺少查询参数"}))
        return
    
    try:
        print(f"处理查询: {query}", file=sys.stderr)
        
        # 步骤1: 规划搜索
        print("执行规划搜索...", file=sys.stderr)
        planning_result = planning_handler({"query": query}, None)
        searches = planning_result.get('searches', [])
        
        # 步骤2: 执行搜索
        print(f"执行{len(searches)}个搜索...", file=sys.stderr)
        search_results = []
        for i, search_item in enumerate(searches):
            print(f"  搜索 {i+1}/{len(searches)}: {search_item['query']}", file=sys.stderr)
            search_result = search_handler({
                "searchTerm": search_item['query'],
                "reason": search_item['reason']
            }, None)
            if 'summary' in search_result:
                search_results.append(search_result['summary'])
        
        # 步骤3: 执行分析
        print("执行分析...", file=sys.stderr)
        analysis_result = analysis_handler({
            "query": query,
            "searchResults": search_results
        }, None)
        fundamentals_analysis = analysis_result.get('fundamentals', '')
        risk_analysis = analysis_result.get('risks', '')
        
        # 步骤4: 生成报告
        print("生成报告...", file=sys.stderr)
        report_result = report_handler({
            "query": query,
            "searchResults": search_results,
            "fundamentalsAnalysis": fundamentals_analysis,
            "riskAnalysis": risk_analysis
        }, None)
        
        # 步骤5: 验证报告
        print("验证报告...", file=sys.stderr)
        verification_result = verification_handler({
            "report": report_result['markdownReport']
        }, None)
        
        # 构建响应
        response = {
            "report": report_result,
            "verification": verification_result
        }
        
        print(json.dumps(response))
    
    except Exception as e:
        print(f"处理请求时出错: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
