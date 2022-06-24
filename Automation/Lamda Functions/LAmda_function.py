import os
import boto3
from pprint import pprint

AMI = os.environ['AMI']
INSTANCE_TYPE = os.environ['INSTANCE_TYPE']
KEY_NAME = os.environ['KEY_NAME']
SUBNET_ID = os.environ['SUBNET_ID']
REGION = os.environ['REGION']

ec2 = boto3.client('ec2', region_name=REGION)

def lambda_handler(event, context):
    client = boto3.client('ec2')
    status = client.describe_instance_status(IncludeAllInstances = False )
    pprint(status)

    des_instance = client.describe_instances(
        InstanceIds=[
            'i-0b173de68992be71a',
        ]
    )
    public_ip = []    
    
    for reservation in des_instance['Reservations']:
        for instance in reservation['Instances']:
            public_ip.append(instance['PublicIpAddress'])
    
    print(public_ip)
    init_script = """#!/bin/bash
                yum update -y
                amazon-linux-extras install nginx1 -y
                service nginx start"""

    instance = ec2.run_instances(
        ImageId=AMI,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SubnetId=SUBNET_ID,
        MaxCount=1,
        MinCount=1,
        UserData=init_script
    )
    instance_id = instance['Instances'][0]['InstanceId']
    print (instance_id)

    return instance_id