from aws_cdk import Stack, Tags
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_lambda as lambda_
from constructs import Construct


class MyFastAPIStack(Stack):
    def __init__(self, scope: Construct, id: str, lambda_url: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Build and push Docker image to ECR
        docker_image = ecr_assets.DockerImageAsset(
            self, "MyDockerImage", directory="../minimal-fastapi-lambda",
        )

        lambda_fast_api = lambda_.DockerImageFunction(
            self, "FastApiLambda",
            code=lambda_.DockerImageCode.from_ecr(
                docker_image.repository, 
                # tag=docker_image.image_tag,
                tag=docker_image.asset_hash,
            ),
            environment={
                "API_GATEWAY_URL": lambda_url,
            }
        )

        # Create an API Gateway REST API
        api = apigateway.LambdaRestApi(
            self, "FastApiRestApi",
            handler=lambda_fast_api,  # pyright: ignore[reportArgumentType]
            proxy=True  # This enables all routes to be proxied to the Lambda
        )

        _ = api

        # Add cost tracking tag
        Tags.of(self).add("AppManagerCFNStackKey", "MyFastAPIStack")
