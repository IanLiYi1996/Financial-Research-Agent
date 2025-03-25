#!/usr/bin/env python3
import os
from aws_cdk import App
from financial_research_stack import FinancialResearchStack

app = App()

# 创建Financial Research Stack
FinancialResearchStack(app, "FinancialResearchStack",
    env={
        "account": os.environ.get("CDK_DEFAULT_ACCOUNT", ""),
        "region": os.environ.get("CDK_DEFAULT_REGION", "us-east-1")
    }
)

app.synth()
