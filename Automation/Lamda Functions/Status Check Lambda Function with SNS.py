import boto3
import json
import os
import time
client = boto3.client('ec2')
ec2 = boto3.resource('ec2')
sns_client = boto3.client('sns')
AMI = os.environ['AMI']
INSTANCE_TYPE = os.environ['INSTANCE_TYPE']
KEY_NAME = os.environ['KEY_NAME']
SUBNET_ID = os.environ['SUBNET_ID']

def lambda_handler(event, context):
 
    running_instances = client.describe_instances(
      Filters = [{
         'Name': 'tag:Name',
         'Values': ['twowayproxy']
       },
      ]
    )
    
    instance_ids = []    
    
    for reservation in running_instances['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
    print(instance_ids)
    
    instance_idss=''.join(instance_ids)
    
    ins_status = client.describe_instance_status(
      InstanceIds=[
          instance_idss,
      ],
  )
    impaired_instance = ins_status['InstanceStatuses'][0]['InstanceStatus']['Status']
    if impaired_instance == 'impaired':
        
        print('Instance Status Check is Impaired')
        message = "Instance was impaired.New Instance has been created now"
        response = sns_client.publish(
        TargetArn="arn:aws:sns:eu-west-1:915754239462:Lamda",
        Message=message,
        MessageStructure='text',
        Subject='Attention Needed',
    )    
        response = client.stop_instances(
    InstanceIds=[
        instance_idss,
    ],
)
       
        print('Impaired Instance has been stopped:', instance_idss)      
        
        response = client.delete_tags(
        Resources=[
        instance_idss,
    ],
    Tags=[
        {
            'Key': 'Name',
            'Value': 'twowayproxy'
        },
    ]
)
        instance = ec2.create_instances(
            ImageId=AMI,
            InstanceType=INSTANCE_TYPE,
            KeyName=KEY_NAME,
            SubnetId=SUBNET_ID,
            MaxCount=1,
            MinCount=1
                 
        )    
        
        print("New instance has been created:", instance[0].id)
       # print(instance[0].id)
        response = ec2.create_tags(
        Resources=[
        instance[0].id,      
    ],
    Tags=[
        {
            'Key': 'Name',
            'Value': 'twowayproxy'
        },
        
    ]
)
        time.sleep(45)
        response = client.associate_address(
    AllocationId='eipalloc-0ae44feb8c1d21915',
    InstanceId=instance[0].id,
    )
        print('Elastic IP has been associated with New Instance')
    else:
        print('Instance Status Check is OK')
        

    
    
    
