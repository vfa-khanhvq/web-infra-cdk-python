#!/usr/bin/env python3
import os

import aws_cdk as cdk
from infra import VpcNetWorkStack, Ec2InstanceStack

app = cdk.App()
vpc_stack = VpcNetWorkStack(app,'VpcNetworkStack')
ec2_stack = Ec2InstanceStack(app,'InstanceStack', vpc_stack.vpc)
ec2_web = ec2_stack.create_load_balance('web instance','infra/scripts/web_start.sh')
ec2_admin = ec2_stack.create_ec2('admin instance')
ec2_stack.add_dependency(vpc_stack)
app.synth()
