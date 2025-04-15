#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_project.basic_lambda_stack import LambdaStack
from cdk_project.fargate_stack import MyFargateStack

app = cdk.App()

# env=cdk.Environment(
#     account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
# ),
env = cdk.Environment(account="572921894147", region="us-west-2")

lambda_stack = LambdaStack(
    app,
    "LambdaStack",
    env=env,
)
MyFargateStack(
    app,
    "MyFargateStack",
    env=env,
    lambda_url=lambda_stack.api_url,
)

app.synth()
