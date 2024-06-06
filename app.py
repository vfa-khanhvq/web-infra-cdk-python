#!/usr/bin/env python3
import os

import aws_cdk as cdk
from infra import VpcNetWorkStack, Ec2InstanceStack, StorageStack

app = cdk.App()
vpc_stack = VpcNetWorkStack(app,'VpcNetworkStack')
vpc = vpc_stack.vpc
ec2_stack = Ec2InstanceStack(app,'InstanceStack', vpc)
ec2_admin = ec2_stack.create_ec2('admin-instance')
ec2_web = ec2_stack.create_load_balance('web-instance','infra/scripts/web_start.sh')
s3_stack = StorageStack(app,'web-front-end', vpc)
s3_bucket = s3_stack.create_s3_bucket('images')
ec2_stack.add_dependency(s3_stack)
ec2_stack.add_dependency(vpc_stack)
app.synth()
