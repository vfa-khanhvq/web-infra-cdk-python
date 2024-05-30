from aws_cdk import (
    App, CfnOutput, Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct
class Ec2InstanceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.vpc = vpc
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
        
    def create_ec2(self, name):
        # Instance
        instance = ec2.Instance(self, name,
            instance_type=ec2.InstanceType("t3.nano"),
            machine_image=self.amzn_linux,
            vpc = self.vpc,
            role = self.role
            )
        return instance
    
    def create_auto_scale(self, name, sh_path, load_balancer_sg):
        # Security Group for Web Instance
        web_instance_sg = ec2.SecurityGroup(self, "InstanceSG " + name,
                                            vpc=self.vpc,
                                            description="Allow HTTP access only from the Load Balancer",
                                            allow_all_outbound=True
                                            )

        web_instance_sg.add_ingress_rule(load_balancer_sg, ec2.Port.tcp(80), "Allow HTTP from Load Balancer")
        # Set user data
        data = open(sh_path, "rb").read()
        user_data=ec2.UserData.for_linux()
        user_data.add_commands(str(data,'utf-8'))

        asg = autoscaling.AutoScalingGroup(
            self,
            "ASG " + name,
            vpc = self.vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2,
                ec2.InstanceSize.MICRO
            ),
            machine_image=self.amzn_linux,
            user_data=user_data,
            role = self.role,
            max_capacity = 1,
            security_group=web_instance_sg

        )
        return asg
    
    def create_load_balance(self, name, sh_path):
        # Security Group for Load Balancer
        load_balancer_sg = ec2.SecurityGroup(self, "LoadBalancerSG " + name,
                                             vpc=self.vpc,
                                             description="Allow HTTP and HTTPS access from anywhere",
                                             allow_all_outbound=True
                                             )
        load_balancer_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP from anywhere")
        load_balancer_sg.add_ingress_rule(ec2.Peer.any_ipv6(), ec2.Port.tcp(80), "Allow HTTP from anywhere (IPv6)")
        load_balancer_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "Allow HTTPS from anywhere")
        load_balancer_sg.add_ingress_rule(ec2.Peer.any_ipv6(), ec2.Port.tcp(443), "Allow HTTPS from anywhere (IPv6)")
        # Load balancer
        lb = elbv2.ApplicationLoadBalancer(
            self,
            "LoadBalancer " + name,
            vpc=self.vpc,
            security_group=load_balancer_sg,
            internet_facing=True)

        asg = self.create_auto_scale(name, sh_path, load_balancer_sg)
        listener = lb.add_listener("Listener", port=80)
        listener.add_targets("Target", port=80, targets=[asg])
        listener.connections.allow_default_port_from_any_ipv4("Open to the world")
        asg.scale_on_request_count("AModestLoad", target_requests_per_minute=60)
