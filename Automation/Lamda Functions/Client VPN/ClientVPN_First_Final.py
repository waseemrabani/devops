import boto3
import json
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
AssociationID = os.environ['association_Id']
SubnetID = os.environ['Subnet_ID']
def lambda_handler(event, context):
#### Deleting perivously created table and creating new DynamoDB table
    response = put_db.delete_table(
    TableName='AllRoutesVPN'
  )
    time.sleep(3)
##Creating DynamoDB Table with two Attributes CIDR and Description CIDR will be identity key.    
    table = put_db.create_table(
        TableName='AllRoutesVPN',
        KeySchema=[
            {​
                'AttributeName': 'CIDR',
                'KeyType': 'HASH'
            }​,
            {​
                'AttributeName': 'Descriptions',
                'KeyType': 'RANGE'
            }​,
        ],
        AttributeDefinitions=[
            {​
                'AttributeName': 'CIDR',
                'AttributeType': 'S'
            }​,
            {​
                'AttributeName': 'Descriptions',
                'AttributeType': 'S'
            }​,
        ],
        ProvisionedThroughput={​
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1,
        }​
    )
    print("Routes Table deleted and created new")
    time.sleep(7)
    # # # #Taking Backup of Routes and Routes Description in DynamoDB Table
    response = client.describe_client_vpn_routes(
    ClientVpnEndpointId=ClientVPNid,
)
    length = len(response ['Routes']) 
    print('Lenght is', length)
    Desc_Array = []
    Cidr_Array = []
    for Dest_CIDR in response ['Routes']:
        Describe = Dest_CIDR ['Description']
        if Describe == "Default Route":
            print(Describe)
        else:
            des_cider = Dest_CIDR ['DestinationCidr']
            Cidr_Array.append(des_cider)
            #Dest_CIDRr = Dest_CIDR ['Description']
            Desc_Array.append(Describe)
    print("Description is",Desc_Array)
    print("DestinationCidr is",Cidr_Array)
    # print_type = type(Desc_Array)
    # print(print_type)
    lenght = len(Desc_Array)   
    print(lenght)
    count = 0
    while count < lenght:
        print(Desc_Array[count])
        print(Cidr_Array[count])
        response = put_db.put_item(
        TableName='AllRoutesVPN',
            Item={​
                'CIDR': {​
                'S':Cidr_Array[count],
                     }​,
                'Descriptions': {​
                'S':Desc_Array[count]
                }​
                }​
            ) 
        count += 1
# ### Disassociating Target Network  
    response_disassociate = client.disassociate_client_vpn_target_network(
    ClientVpnEndpointId=ClientVPNid,
    AssociationId= AssociationID,
    )
    print ('Target Network has been Disassociated')
## Reassociating Target Network
    response_associate = client.associate_client_vpn_target_network(
    ClientVpnEndpointId=ClientVPNid,
    SubnetId=SubnetID
)
    print ('Target Network has been Associated')
    assoc_id = response_associate['AssociationId']
    print(assoc_id)
    wait_association = client.describe_client_vpn_target_networks(
    ClientVpnEndpointId=ClientVPNid,
)
## Updating Association ID in enviornment variable using Lambda update config function
    response_lambda = client_lambda.update_function_configuration(
    FunctionName='ClientVPN_First',
    Environment={​
        'Variables': {​
            'association_Id': assoc_id,
            'ClientVPN_ID': ClientVPNid,
            'Subnet_ID':SubnetID
        }​
    }​,
)
