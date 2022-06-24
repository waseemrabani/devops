import boto3
import json
#import string
client = boto3.client('ec2')
def lambda_handler(event, context):
    response = client.create_client_vpn_route(
    ClientVpnEndpointId='cvpn-endpoint-0294b7061064e1952',
    DestinationCidrBlock='11.12.0.0/20', 
    TargetVpcSubnetId='subnet-f5e5cabd',
    Description='Test',
)
    return(response)