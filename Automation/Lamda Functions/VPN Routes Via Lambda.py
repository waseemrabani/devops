import boto3
import json
from boto3.dynamodb.conditions import Key
import json
import os
client_lambda = boto3.client('lambda')
client = boto3.client('ec2')
put_db = boto3.client('dynamodb')  
scan_db = boto3.resource('dynamodb')
AssociationId = os.environ['AssociationId']

def lambda_handler(event, context):
    
    response = client.describe_client_vpn_routes(
    ClientVpnEndpointId='cvpn-endpoint-0be48f1d74b1ef899',
    
)
    responselen = len(response ['Routes']) 

    print('responselen', responselen)
    x = []
    for Dcider in response ['Routes']:
        Dciderr = Dcider ['DestinationCidr']
        x.append(Dciderr)
        print(x)
        print_type = type(x)
    print(print_type)
    for y in x:
        print(y)
        printt_type = type(y)
        print(printt_type)
        response_db=put_db.put_item(TableName='Routes', Item={'CIDR':{'S':y},})
    print("Routes Stored in Dynamodb")
    response_disassociate = client.disassociate_client_vpn_target_network(
    ClientVpnEndpointId='cvpn-endpoint-0be48f1d74b1ef899',
    AssociationId= AssociationId,
    )
    print ('Target Network has been Disassociated')
    
    response_associate = client.associate_client_vpn_target_network(
    ClientVpnEndpointId='cvpn-endpoint-0be48f1d74b1ef899',
    SubnetId='subnet-f5e5cabd',
   
)
    print ('Target Network has been Associated')
    assoc_id = response_associate['AssociationId']
    print(assoc_id)
    response_lambda = client_lambda .update_function_configuration(
    FunctionName='Associstion',
    Environment={
        'Variables': {
            'AssociationId': assoc_id
        }
    },
)
  # print ('association id ')
    
    print('AssociationId', assoc_id)
#     return(assoc_id)
    table = scan_db.Table("Routes")
    response = table.scan()
    result = response['Items']
    for result in response ['Items']:
        results = result ['CIDR']
    print(results)
    
#     response = put_db.delete_item(
#     TableName='Routes',
#     Key={
#         'CIDR': {
#             'S': results,
#             }
#         }    
#     )
#     # res_type = type(result)
#     # print(res_type)    
#     # convert_str = str(result)
#     # print_type = type(convert_str)
#     # print(print_type)
    
#     time.sleep(600)
    response = client.create_client_vpn_route(
    ClientVpnEndpointId='cvpn-endpoint-0be48f1d74b1ef899',
    DestinationCidrBlock=results,
    TargetVpcSubnetId='subnet-f5e5cabd',
    Description='Test',
)