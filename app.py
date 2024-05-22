#!/usr/bin/env python3
import os

import aws_cdk as cdk
from infra import VpcNetWorkStack, Ec2InstanceStack

app = cdk.App()
vpc_stack = VpcNetWorkStack(app,'VpcNetworkStack')
ec2_stack = Ec2InstanceStack(app,'InstanceStack')
ec2_stack.create_ec2(vpc_stack.vpc, 'web instance')
ec2_stack.add_dependency(vpc_stack)
app.synth()
