import requests
import boto3
import time
import json
import os

#Enviornment Vaiables
CloudFlareURL = os.environ['URL']
PrefixListID = os.environ['prefixlist_Id']
#Boto Client
client = boto3.client('ec2')
def lambda_handler(event, context):
#Getting IP list from CloudFlare
    headers = {
        'Content-type': 'application/json',
    }
    url = CloudFlareURL
    r = requests.get(url, headers=headers)
    #Removing /n from IP List
    temp = r.text
    cloudflare_IP_list = [y for y in (x.strip() for x in temp.splitlines()) if y] 
    print ("CloudFlare IP list",cloudflare_IP_list)
    
    #Getting IP from already created Managed Prefix List
    prefixlist_response = client.get_managed_prefix_list_entries(
    PrefixListId=PrefixListID,
)
    IP_list = []
    for z in prefixlist_response ['Entries']:
        IPs = z ['Cidr']
        IP_list.append(IPs)
        print("Existing IP list",IPs )
    into_list = list(IP_list)
    print("String Converted into List",into_list)
    
    
    total_lenght = len(IP_list)
    print("Length is",total_lenght)

     #Getting Prefix List Version Number in a variable
    target_response = client.describe_managed_prefix_lists(
    PrefixListIds=[PrefixListID,
    ]
)
    current_version =  target_response ['PrefixLists'][0]['Version']
    print("Current Version is",current_version)

#Comparing two lists of IP geted from Cloudflare and already created managed prefix list
    # l = len(results)
    list1 = cloudflare_IP_list
    list2 = into_list
    
    compared_list = []
    for ip1 in list1:
        for ip2 in list2:
            if ip1 == ip2:
                print("IP Matched")
                break
        if ip1 != ip2:
            print("IP Not Matched")
            compared_list.append(ip1)
            print(compared_list)
    print("New IP Found",compared_list)

   
    #Converting list into Json
    list_to_json = json.dumps(compared_list)
    #print(list_to_json)
    
    if not compared_list:
        print("No new cloudflare IP found")
        return()
        
    
    list_json=[]
    for result in compared_list:
        list_json.append({
                'Cidr': result,
                'Description': 'CloudFlare'
         })
    #print (list_json)
    #Adding IP List into Desire Managed Prefix list
    response = client.modify_managed_prefix_list(
    PrefixListId=PrefixListID,
    CurrentVersion=current_version,
    AddEntries=list_json
       
             )