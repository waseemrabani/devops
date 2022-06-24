import json
import boto3
import os
ClientVPNid = os.environ['ClientVPN_ID']
client = boto3.client('ec2')
def lambda_handler(event, context):
    response = client.create_client_vpn_route(
    ClientVpnEndpointId=ClientVPNid,
    DestinationCidrBlock='0.0.0.0/0', 
    TargetVpcSubnetId='subnet-f5e5cabd',
    Description='AllTraffic',
)
    print ('Routes has been Added')