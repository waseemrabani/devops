import boto3
import json
from boto3.dynamodb.conditions import Key
import os
import time
client_lambda = boto3.client('lambda')
client = boto3.client('ec2')
put_db = boto3.client('dynamodb')  
scan_db = boto3.resource('dynamodb')
#AssociationId = os.environ['Association_Id']
ClientVPNid = os.environ['ClientVPN_ID']

def lambda_handler(event, context):
   
# #Getting Stored Routes from DynamoDb Table
    table = scan_db.Table("Routes")
    response = table.scan()
#    return(response)
    result = response['Items']
    n = []
    for result in response ['Items']:
        results = result ['CIDR']
        n.append(results)
    print(n)
    
    resul = response['Items']
    m = []
    for resul in response ['Items']:
        resu = resul ['Descriptions']
        m.append(resu)
    print(m)
#     #print(results)
    
    ## Adding Routes back to CLient 
    scan_length = len(m)
    print("Length of scan is",scan_length)
    
    
    count = 0
    while count < scan_length:
        print(n[count])
        print(m[count])
        response = client.create_client_vpn_route(
        ClientVpnEndpointId=ClientVPNid,
        DestinationCidrBlock=n[count],
        TargetVpcSubnetId='subnet-f5e5cabd',
        Description=m[count],
 )
        count += 1
        print("Routes has been Added ")
    
        
   