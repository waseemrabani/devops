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
SubnetID = os.environ['Subnet_ID']
def lambda_handler(event, context):
   
# #Getting Stored Routes and Routes Description from DynamoDb Table
    
    table = scan_db.Table("Routes")
    response = table.scan()
    result = response['Items']
    scan_cidr = []
    scan_desc = []
    for result in response ['Items']:
        results = result ['CIDR']
        scan_cidr .append(results)
        print(scan_cidr )
        result_Des = result ['Descriptions']
        scan_desc .append(result_Des)
        print(scan_desc )

    
    ## Adding Routes and Routes Description back to CLient 
    
    scan_length = len(scan_desc )
    print("Length of scan is",scan_length)
    
    count = 0
    while count < scan_length:
        print(scan_cidr [count])
        print(scan_desc [count])
        response = client.create_client_vpn_route(
        ClientVpnEndpointId=ClientVPNid,
        DestinationCidrBlock=scan_cidr[count],
        TargetVpcSubnetId=SubnetID,
        Description=scan_desc[count],
  )
        count += 1
        if count%5 == 0:
            time.sleep(120)
        else:
        
            print("Routes has been Added ")
    
        
   
   