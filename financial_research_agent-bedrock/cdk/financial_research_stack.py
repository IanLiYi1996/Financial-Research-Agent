from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_iam as iam,
    Duration,
    CfnOutput,
    RemovalPolicy
)
from constructs import Construct
import os

try:
    from aws_cdk.aws_bedrock_alpha import (
        CfnAgent,
        CfnAgentAlias,
        CfnKnowledgeBase
    )
    BEDROCK_ALPHA_AVAILABLE = True
except ImportError:
    print("Warning: aws_cdk.aws_bedrock_alpha is not available. Using placeholder classes.")
    BEDROCK_ALPHA_AVAILABLE = False
    
    class CfnAgent:
        pass
    
    class CfnAgentAlias:
        pass
    
    class CfnKnowledgeBase:
        pass


class FinancialResearchStack(Stack):
    """
    AWS CDK Stack for Financial Research Agent using AWS Bedrock
    """
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # 创建S3存储桶用于存储金融文档
        documents_bucket = s3.Bucket(
            self, "FinancialDocumentsBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        # 创建Lambda执行角色
        lambda_role = iam.Role(
            self, "FinancialResearchLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
            ]
        )
        
        # 添加S3访问权限
        documents_bucket.grant_read_write(lambda_role)
        
        # 创建Lambda层，包含共享代码和依赖
        lambda_layer = lambda_.LayerVersion(
            self, "FinancialResearchLambdaLayer",
            code=lambda_.Code.from_asset("../lambdas/layer"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            description="Common libraries for Financial Research Agent"
        )
        
        # 创建Lambda函数
        orchestrator_lambda = self._create_lambda(
            "OrchestratorLambda", 
            "../lambdas/orchestrator", 
            "handler.lambda_handler",
            lambda_role,
            lambda_layer
        )
        
        planning_lambda = self._create_lambda(
            "PlanningLambda", 
            "../lambdas/planning", 
            "handler.lambda_handler",
            lambda_role,
            lambda_layer
        )
        
        search_lambda = self._create_lambda(
            "SearchLambda", 
            "../lambdas/search", 
            "handler.lambda_handler",
            lambda_role,
            lambda_layer
        )
        
        analysis_lambda = self._create_lambda(
            "AnalysisLambda", 
            "../lambdas/analysis", 
            "handler.lambda_handler",
            lambda_role,
            lambda_layer
        )
        
        report_lambda = self._create_lambda(
            "ReportLambda", 
            "../lambdas/report", 
            "handler.lambda_handler",
            lambda_role,
            lambda_layer
        )
        
        verification_lambda = self._create_lambda(
            "VerificationLambda", 
            "../lambdas/verification", 
            "handler.lambda_handler",
            lambda_role,
            lambda_layer
        )
        
        # 设置Lambda环境变量
        orchestrator_lambda.add_environment("PLANNING_LAMBDA", planning_lambda.function_name)
        orchestrator_lambda.add_environment("SEARCH_LAMBDA", search_lambda.function_name)
        orchestrator_lambda.add_environment("ANALYSIS_LAMBDA", analysis_lambda.function_name)
        orchestrator_lambda.add_environment("REPORT_LAMBDA", report_lambda.function_name)
        orchestrator_lambda.add_environment("VERIFICATION_LAMBDA", verification_lambda.function_name)
        
        # 授予Lambda调用其他Lambda的权限
        planning_lambda.grant_invoke(orchestrator_lambda)
        search_lambda.grant_invoke(orchestrator_lambda)
        analysis_lambda.grant_invoke(orchestrator_lambda)
        report_lambda.grant_invoke(orchestrator_lambda)
        verification_lambda.grant_invoke(orchestrator_lambda)
        
        # 创建API Gateway
        api = apigateway.RestApi(
            self, "FinancialResearchApi",
            rest_api_name="Financial Research API",
            description="API for Financial Research Agent"
        )
        
        # 添加API资源和方法
        research_resource = api.root.add_resource("research")
        research_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(orchestrator_lambda)
        )
        
        # 如果Bedrock Alpha CDK构造可用，创建Bedrock资源
        if BEDROCK_ALPHA_AVAILABLE:
            # 创建Knowledge Base角色
            kb_role = iam.Role(
                self, "KnowledgeBaseRole",
                assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com")
            )
            
            documents_bucket.grant_read(kb_role)
            
            # 创建Knowledge Base
            knowledge_base = CfnKnowledgeBase(
                self, "FinancialKnowledgeBase",
                name="FinancialKnowledgeBase",
                description="Knowledge base for financial research",
                knowledge_base_configuration={
                    "type": "VECTOR",
                    "vectorKnowledgeBaseConfiguration": {
                        "embeddingModelArn": f"arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v1"
                    }
                },
                storage_configuration={
                    "type": "S3",
                    "s3Configuration": {
                        "bucketArn": documents_bucket.bucket_arn
                    }
                },
                role_arn=kb_role.role_arn
            )
            
            # 创建Bedrock Agent角色
            agent_role = iam.Role(
                self, "BedrockAgentRole",
                assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com")
            )
            
            # 创建Bedrock Agent
            agent = CfnAgent(
                self, "FinancialResearchAgent",
                agent_name="FinancialResearchAgent",
                agent_resource_role_arn=agent_role.role_arn,
                foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
                instruction="你是一个金融研究助手，专门分析公司财务状况、行业趋势和市场动态。你可以回答有关公司财务表现、风险分析和投资机会的问题。",
                customer_encryption_key_arn=None,  # 可选：使用KMS密钥进行加密
                description="Financial Research Agent powered by AWS Bedrock",
                idle_session_ttl_in_seconds=1800  # 30分钟超时
            )
            
            # 创建Agent别名
            agent_alias = CfnAgentAlias(
                self, "FinancialResearchAgentAlias",
                agent_id=agent.attr_agent_id,
                agent_alias_name="prod",
                routing_configuration=[{
                    "agent_version": "DRAFT"
                }]
            )
            
            # 添加Knowledge Base到Agent
            if hasattr(knowledge_base, "attr_knowledge_base_id"):
                # 注意：这里需要使用AWS CLI或控制台将Knowledge Base添加到Agent
                # CDK目前不直接支持这个操作
                CfnOutput(
                    self, "KnowledgeBaseId",
                    value=knowledge_base.attr_knowledge_base_id,
                    description="Knowledge Base ID to be added to the Agent"
                )
            
            # 输出Agent ID和别名
            CfnOutput(
                self, "AgentId",
                value=agent.attr_agent_id,
                description="Bedrock Agent ID"
            )
            
            CfnOutput(
                self, "AgentAliasId",
                value=agent_alias.attr_agent_alias_id,
                description="Bedrock Agent Alias ID"
            )
            
            # 设置Lambda环境变量
            search_lambda.add_environment("KNOWLEDGE_BASE_ID", knowledge_base.attr_knowledge_base_id if hasattr(knowledge_base, "attr_knowledge_base_id") else "")
        
        # 输出API Gateway URL
        CfnOutput(
            self, "ApiUrl",
            value=f"{api.url}research",
            description="API Gateway URL for Financial Research"
        )
        
        # 输出S3存储桶名称
        CfnOutput(
            self, "DocumentsBucketName",
            value=documents_bucket.bucket_name,
            description="S3 Bucket for Financial Documents"
        )
    
    def _create_lambda(self, id: str, code_path: str, handler: str, role: iam.Role, layer: lambda_.LayerVersion = None) -> lambda_.Function:
        """创建Lambda函数的辅助方法"""
        function = lambda_.Function(
            self, id,
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset(code_path),
            handler=handler,
            role=role,
            timeout=Duration.seconds(300),
            memory_size=512
        )
        
        if layer:
            function.add_layers(layer)
            
        return function
