import boto3
import json
import time
import os
#Enviornment Vaiables
TGARN = os.environ['TG_ARN']
TopicARN = os.environ['Topic_ARN']
REGION = os.environ['RegionName']
put_db = boto3.client('dynamodb')  
scan_db = boto3.resource('dynamodb')
sns_client = boto3.client('sns')
results = []
unhealthy = []
client = boto3.client('ec2', region_name=REGION)
#regions = client.describe_regions()['Regions']

def lambda_handler(event, context):
    # for region in regions:
        
    elb = boto3.client('elbv2', region_name=REGION)
    tgh = elb.describe_target_health(
TargetGroupArn=TGARN,
)
#Getting target group health and instance ID
    for t in tgh['TargetHealthDescriptions']:

        if 'State' in t['TargetHealth']:
            resultt = t['TargetHealth']['State']
            
            print("Instances are",resultt)
        if 'Id' in t['Target']:
            resultts = t['Target']['Id']
            #print("Id of instance is",resultts)
            if (resultt == "healthy"):
                results.append(t['Target']['Id'])
    
            if (resultt == "unhealthy"):
                instanceID = t['Target']['Id']
                unhealthy.append(instanceID)
                print ("Unhealthy InstanceID is", instanceID)
                
                
                #print("These instances are unhealthy")
          
                
                response = client.stop_instances(
                    InstanceIds=[
                    instanceID,
    ],
                
)
                #To send email notification 
                
                message = "Combain Instance has been stopped.Kindly check"
                sns_response = sns_client.publish(
                TargetArn=TopicARN,
                Message=message,
                MessageStructure='text',
                Subject='Combain server Unhealthy',
            )
                print("Email sent")
    for ids in unhealthy:
        response = put_db.put_item(
        TableName='InstanceID',
        Item={
            'ID': {
            'S':ids,
                },
        
        }
    )
   