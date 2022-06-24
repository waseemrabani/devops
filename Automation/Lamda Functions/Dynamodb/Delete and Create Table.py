import boto3
import json
import time
from boto3.dynamodb.conditions import Key
client = boto3.client('ec2')
put_db = boto3.client('dynamodb')  
def lambda_handler(event, context):
    # Delete Dynamodb Table
    response = put_db.delete_table(
    TableName='Routes'
  )

    time.sleep(3)
	
	#Create Dynamodb Table
	
    #### Deleting perivously created table and creating new DynamoDB table
    response = put_db.delete_table(
    TableName='Routes'
  )

    time.sleep(3)
    
    
##Creating DynamoDB Table with two Attributes CIDR and Description CIDR will be identity key.    
    table = put_db.create_table(
        TableName='Routes',
        KeySchema=[
            {
                'AttributeName': 'CIDR',
                'KeyType': 'HASH'
            },
            
            {
                'AttributeName': 'Descriptions',
                'KeyType': 'RANGE'
            },
            
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'CIDR',
                'AttributeType': 'S'
            },
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
