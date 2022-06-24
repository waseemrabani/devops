#Uhealthy Instance check in Target Group
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
    tgh = elb.describe_target_health(
TargetGroupArn='arn:aws:elasticloadbalancing:eu-central-1:409947039396:targetgroup/dev-default-tg/ccd48339c01764ce',
)
    print(tgh)
    for t in tgh['TargetHealthDescriptions']:
        result = {'id': t['Target']['Id'], 'port': t['Target']['Port'], 'state': t['TargetHealth']['State'], 'reason': ""}
        print(result)
        if 'State' in t['TargetHealth']:
            health = t['TargetHealth']['State']
            
            print("Heath of Instance is",health)
        if 'Id' in t['Target']:
            resultts = t['Target']['Id']
            print("Id of instance is",resultts)
            if (health == "healthy"):
                results.append("Instance {} on port {} reported {} status. Reason: {}".format(result['id'], result['port'], result['state'], result['reason']))    
                print("All instances are healthy")
        
            if (health != "healthy"):
                results.append("Instance {} on port {} reported {} status. Reason: {}".format(result['id'], result['port'], result['state'], result['reason']))
                
                print("These instances are unhealthy")
                print("IDS are", result['id'])
                response = client.stop_instances(
            InstanceIds=[
                result['id'],
    ],
                
)   
                print("Instance", result['id'],"have been stopped." )
                
                ### Deleting perivously created table and creating new DynamoDB table
                response = put_db.delete_table(
                TableName='InstanceID'
                )
                time.sleep(3)
                #Creating DynamoDB Table with two Attributes CIDR and Description CIDR will be identity key.    
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
                time.sleep(7)
                #Adding unhealthy Instance ID into dynamodb
                response = put_db.put_item(
                TableName='InstanceID',
                Item={
                    'ID': {
                    'S':resultts,
                        },
                }
            ) 
                #Getting unhealthy Instance ID from Dynamodb

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
                time.sleep(60)
                
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
                   