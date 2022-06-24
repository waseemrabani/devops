import boto3
import json
from boto3.dynamodb.conditions import Key
import os
import time
client_lambda = boto3.client('lambda')
client = boto3.client('ec2')
put_db = boto3.client('dynamodb')  
scan_db = boto3.resource('dynamodb')
ClientVPNid = os.environ['ClientVPN_ID']


def lambda_handler(event, context):
    
# # # #Taking Backup of Routes Description in DynamoDB
   
    response = put_db.delete_table(
    TableName='Description'
  )

    time.sleep(3)
    table = put_db.create_table(
        TableName='Description',
        KeySchema=[
            {
                'AttributeName': 'Descriptions',
                'KeyType': 'HASH'
            },
            
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Descriptions',
                'AttributeType': 'S'
            },
            
            
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1,
        }
    )
    print(table)
    time.sleep(7)
    response = client.describe_client_vpn_routes(
    ClientVpnEndpointId=ClientVPNid,
    
)
    responselen = len(response ['Routes']) 

    print('responselen', responselen)
    x = []
    for Dcider in response ['Routes']:
        Dciderrs = Dcider ['Description']
        if Dciderrs == "Default Route":
            print(Dciderrs)
        else:
            
            Dciderr = Dcider ['Description']
            x.append(Dciderr)
            print(x)
    print_type = type(x)
    print(print_type)
    
    for y in x:
        print(y)
        #printt_type = type(y)
        #print(printt_type)
        response_db=put_db.put_item(TableName='Description', Item={'Descriptions':{'S':y},})
    print("Routes Stored in Dynamodb")
    
    response = put_db.delete_table(
    TableName='Routes'
  )

    time.sleep(3)
    table = put_db.create_table(
        TableName='Routes',
        KeySchema=[
            {
                'AttributeName': 'CIDR',
                'KeyType': 'HASH'
            },
            
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'CIDR',
                'AttributeType': 'S'
            },
            
            
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1,
        }
    )
    response = client.describe_client_vpn_routes(
    ClientVpnEndpointId=ClientVPNid,
    
)
    responselen = len(response ['Routes']) 

    print('responselen', responselen)
    c = []
    for Dcider in response ['Routes']:
        Dcide = Dcider ['Description']
        if Dcide == "Default Route":
            print(Dcide)
        else:
            
            Dcidee = Dcider ['DestinationCidr']
            c.append(Dcidee)
            print(c)
#     print_type = type(x)
#     print(print_type)
    time.sleep(7)
    for z in c:
        print(z)    
        response_db=put_db.put_item(TableName='Routes', Item={'CIDR':{'S':z},})
    print("Description has been Stored in Dynamodb")