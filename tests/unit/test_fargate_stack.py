import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_project.basic_lambda_stack import LambdaStack
from cdk_project.fargate_stack import MyFargateStack


# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_project/cdk_project_stack.py
def test_sqs_queue_created():
    app = core.App()
    env = core.Environment(account="572921894147", region="us-west-2")
    lambda_stack = LambdaStack(
        app,
        "LambdaStack",
        env=env,
    )
    stack = MyFargateStack(app, 
                           "cdk-project", 
                           env=env,
                           lambda_url=lambda_stack.api_url)
    template = assertions.Template.from_stack(stack)


    # template.has_resource_properties("AWS::", {
    #     "VisibilityTimeout": 300
    # })
