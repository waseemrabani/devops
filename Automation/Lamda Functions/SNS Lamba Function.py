import json
import boto3
client = boto3.client('sns')
def lambda_handler(event, context):
        message = "Instance has been impaired.Kindly check"
        response = client.publish(
        TargetArn="arn:aws:sns:eu-west-1:915754239462:Lamda",
        Message=message,
        MessageStructure='text',
        Subject='Attention',
    )    