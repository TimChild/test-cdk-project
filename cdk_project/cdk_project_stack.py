from aws_cdk import Duration, Stack, Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from constructs import Construct


class MyFargateStack(Stack):
    def __init__(self, scope: Construct, id: str, lambda_url: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "MyVpc", max_azs=3)

        # Create an ECS Cluster
        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        # Build and push Docker image to ECR
        docker_image = ecr_assets.DockerImageAsset(
            self, "MyDockerImage", directory="../minimal-fastapi"
        )

        # Use the Docker image in a Fargate service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "MyFargateService",
            cluster=cluster,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_docker_image_asset(docker_image),
                environment={
                    "API_GATEWAY_URL": lambda_url,
                },
            ),
            desired_count=1,
            cpu=256, # 1/4 vCPU (lowest)
            memory_limit_mib=512, # 512 MiB (lowest)
            public_load_balancer=True,
            min_healthy_percent=100,
        )

        fargate_service.target_group.configure_health_check(
            path="/healthcheck",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
            healthy_http_codes="200",
            healthy_threshold_count=2,
            unhealthy_threshold_count=2,
        )

        # Add cost tracking tag
        Tags.of(self).add("AppManagerCFNStackKey", "MyFargateStack")
