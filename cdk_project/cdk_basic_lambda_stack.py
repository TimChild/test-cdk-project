from aws_cdk import Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_lambda as lambda_
from constructs import Construct


class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        hello_lambda = lambda_.Function(
            self,
            "HelloLambda",
            function_name="SimpleHelloLambda",
            description="A simple hello world Lambda function",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="hello.lambda_handler",
            code=lambda_.Code.from_asset("lambdas"),
        )

        api = apigateway.LambdaRestApi(
            self,
            "HelloApi",
            handler=hello_lambda,  # pyright: ignore[reportArgumentType]
            proxy=False,
            rest_api_name="HelloApi",
            description="A simple hello world API",
        )

        hello_resource = api.root.add_resource("hello")
        hello_resource.add_method("GET")  # GET /hello

        self.api_url = api.url
