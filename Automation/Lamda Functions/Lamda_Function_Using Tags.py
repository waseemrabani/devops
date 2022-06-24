import json
import boto3

#
# region_name - the region that should be covered by the scheduler
#
region_name='eu-west-1'

#
# instance_to_check - set the ID of the instance to check
#
instance_to_check = { 'instance_id': 'i-0fdd819f8d1f1a3c6' }


def lambda_handler(event, context):
    ec2 = boto3.resource('ec2', region_name=region_name)
    ec2_client = boto3.client('ec2', region_name=region_name)
    
    for status in ec2.meta.client.describe_instance_status(
          InstanceIds=[ instance_to_check['instance_id'] ]
        )['InstanceStatuses']:
            
        in_status = status['InstanceStatus']['Details'][0]['Status']
        sys_status = status['SystemStatus']['Details'][0]['Status']
      
        # check statuses
        if ((in_status != 'passed') or (sys_status != 'passed')):
            print('Reboot required')
            ec2_client.reboot_instances(InstanceIds=[ instance_to_check['instance_id'] ])
  

 


##Check Instance Using tags that isnatnce is found or not
import boto3
ec2 = boto3.resource('ec2')

def lambda_handler(event, context):
    filters = [{
         'Name': 'tag:Name',
         'Values': ['Lamda-Test']
       },
       {
        'Name': 'tag:App',
        'Values': ['Yap-testing']
     }]

    instances = ec2.instances.filter(Filters=filters)

    RunningInstances = [instance.id for instance in instances]
    
    if len(RunningInstances) > 0:
       print("found instances with tag")
    else:
        print("no instance found")


 ##Reboot Instance when status check failed
########
import json
import boto3
#
# region_name - the region that should be covered by the scheduler
#
region_name='eu-west-1'
#
# instance_to_check - set the ID of the instance to check
#
instance_to_check = { 'instance_id': 'i-0fdd819f8d1f1a3c6' }
def lambda_handler(event, context):
    ec2 = boto3.resource('ec2', region_name=region_name)
    ec2_client = boto3.client('ec2', region_name=region_name)
    
    for status in ec2.meta.client.describe_instance_status(
          InstanceIds=[ instance_to_check['instance_id'] ]
        )['InstanceStatuses']:
            
        in_status = status['InstanceStatus']['Details'][0]['Status']
        sys_status = status['SystemStatus']['Details'][0]['Status']
      
        # check statuses
        if ((in_status != 'passed') or (sys_status != 'passed')):
            print('Reboot required')
            ec2_client.reboot_instances(InstanceIds=[ instance_to_check['instance_id'] ])


##Get Instance ID using Tags

import boto3
import json
from collections import defaultdict

region = 'eu-west-1'

def lambda_handler(event, context):
    
    client = boto3.client('ec2')

    running_instances = client.describe_instances(
      Filters = [{
         'Name': 'tag:Name',
         'Values': ['Lamda-Test']
       },
       {
        'Name': 'tag:App',
        'Values': ['Yap-testing']
     }]
    
    )
    
    instance_ids = []    
    
    for reservation in running_instances['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
    print(instance_ids)
    

    return instance_ids
