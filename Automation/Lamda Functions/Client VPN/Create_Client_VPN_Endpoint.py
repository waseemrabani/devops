import json
import boto3
client = boto3.client('ec2')

def lambda_handler(event, context):
    response = client.create_client_vpn_endpoint(
    ClientCidrBlock='10.10.0.0/20',
    ServerCertificateArn='arn:aws:acm:eu-west-1:915754239462:certificate/89cf2b66-d6c7-4152-a7be-adc78f86e630',
    AuthenticationOptions=[
        {
            'Type': 'certificate-authentication',
           
            'MutualAuthentication': {
                'ClientRootCertificateChainArn': 'arn:aws:acm:eu-west-1:915754239462:certificate/c4e3ef9d-f2e8-405a-9ddd-690e55b668ac'
            },
            
            }
       
    ],
    
    ConnectionLogOptions={
        'Enabled': False,
        
    },
    TransportProtocol='udp',
    VpnPort=443,
    Description='Test',
    SplitTunnel=True,
   
    TagSpecifications=[
        {
            'ResourceType': 'client-vpn-endpoint',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'TestVPN'
                },
            ]
        },
    ],
    SecurityGroupIds=[
        'sg-0948b661ff4c76392',
    ],
    VpcId='vpc-f2e3018b',
    SelfServicePortal='disabled',
    
)