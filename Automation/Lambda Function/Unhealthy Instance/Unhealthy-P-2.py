import boto3
import json
import time
put_db = boto3.client('dynamodb')  
scan_db = boto3.resource('dynamodb')
results = []
client = boto3.client('ec2', region_name='eu-central-1')

def lambda_handler(event, context):
#Getting Unhealthy state and instance ID  from Target Group
    elb = boto3.client('elbv2', region_name='eu-central-1')
    
    table = scan_db.Table("InstanceID")
    response = table.scan()
    result = response['Items']
    scan_id = []
    for a in response ['Items']:
        b = a ['ID']
        scan_id .append(b)
        print(scan_id )
        ty = type(scan_id)
        print(ty)
        into_str = str(scan_id)
        tys = type(into_str)
        print(tys)
        
        #Removing '' and [] frominstance ID
        
        new_list=(', '.join(scan_id))
        print(new_list)
        scan_length = len(scan_id)
        print("Length of scan is",scan_length)
        if scan_length == 0:
            return()
    #starting Unhealthy Instances
        count = 0
        while count < scan_length:
            print(scan_id[count])
            response = client.start_instances(
        InstanceIds=[
            scan_id[count],
        ],
        )             
            count += 1
            print("Instances have been Started")
       
    
    #Creating DynamoDB Table with two Attributes CIDR and Description CIDR will be identity key.    
    
    response = put_db.delete_table(
    TableName='InstanceID'
    )
    time.sleep(3)
    table = put_db.create_table(
        TableName='InstanceID',
        KeySchema=[
            {
                'AttributeName': 'ID',
                'KeyType': 'HASH'
            },
            
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'ID',
                'AttributeType': 'S'
            },
            
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1,
        }
    )
    print("InstanceID Table deleted and created new")
    