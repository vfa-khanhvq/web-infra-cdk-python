import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct
class VpcNetWorkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # if not hasattr(self, 'vpc'):
        self.vpc = ec2.Vpc(self, "VPC",
            nat_gateways=0,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs= 1,
            subnet_configuration=[ec2.SubnetConfiguration(name="public",subnet_type=ec2.SubnetType.PUBLIC),
                                ec2.SubnetConfiguration(name="private",subnet_type=ec2.SubnetType.PRIVATE_ISOLATED, )]
            )
        cdk.CfnOutput(self, 'VPCID', value=self.vpc.vpc_id,
        export_name=f'{self.stack_name}-VPCID')
