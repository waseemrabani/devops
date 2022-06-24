import boto3
import json
from boto3.dynamodb.conditions import Key
import os
import time
import subprocess
import socket
import logging
client_lambda = boto3.client('lambda')
client = boto3.client('ec2')
put_db = boto3.client('dynamodb')  
scan_db = boto3.resource('dynamodb')
ClientVPNid = os.environ['ClientVPN_ID']
SubnetID = os.environ['Subnet_ID']
logger = logging.getLogger()
logger.setLevel(logging.INFO)
def run_command(command):
    command_list = command.split(' ')
    try:
        logger.info("Running shell command: \"{}\"".format(command))
        result = subprocess.run(command_list, stdout=subprocess.PIPE);
        logger.info("Command output:\n---\n{}\n---".format(result.stdout.decode('UTF-8')))
    except Exception as e:
        logger.error("Exception: {}".format(e))
        return False
    return True
def lambda_handler(event, context):
# #Getting Stored Routes and Routes Description from DynamoDb Table
    table = scan_db.Table("AllRoutesVPN")
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
        cidrblock = (scan_cidr [count])
        descriptions = (scan_desc [count])
        print(cidrblock)
        print(descriptions)
        run_command(f"/opt/aws ec2 create-client-vpn-route --client-vpn-endpoint-id {ClientVPNid} --description {descriptions} --destination-cidr-block {cidrblock} --target-vpc-subnet-id {SubnetID}")
        count += 1
        time.sleep(3)