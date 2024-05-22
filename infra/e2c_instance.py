from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct
class Ec2InstanceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        if not hasattr(self, 'amzn_linux'):
            #AMI
            self.amzn_linux = ec2.MachineImage.latest_amazon_linux(
                    generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                    edition=ec2.AmazonLinuxEdition.STANDARD,
                    virtualization=ec2.AmazonLinuxVirt.HVM,
                    storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
                    )
        if not hasattr(self, 'role'):
            # Instance Role and SSM Managed Policy
            self.role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
            self.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        
    def create_ec2(self, vpc, name):
        # Instance
        instance = ec2.Instance(
            self,
            name,
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            vpc=vpc,
            associate_public_ip_address=False,
        )
        return instance