#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_project.basic_lambda_stack import LambdaStack

# from cdk_project.fargate_stack import MyFargateStack
from cdk_project.fast_api_stack import MyFastAPIStack

app = cdk.App()

env = cdk.Environment(account="572921894147", region="us-west-2")

lambda_stack = LambdaStack(
    app,
    "LambdaStack",
    env=env,
)
# MyFargateStack(
#     app,
#     "MyFargateStack",
#     env=env,
#     lambda_url=lambda_stack.api_url,
# )
MyFastAPIStack(
    app,
    "MyFastAPIStack",
    env=env,
    lambda_url=lambda_stack.api_url,
)


app.synth()
