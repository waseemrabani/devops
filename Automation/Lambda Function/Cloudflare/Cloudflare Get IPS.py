import requests
import boto3
import time
import json
import os
CloudFlareURL = os.environ['URL']
PrefixListID = os.environ['association_Id']
ClientVPNid = os.environ['ClientVPN_ID']
AssociationID = os.environ['association_Id']
client = boto3.client('ec2')
put_db = boto3.client('dynamodb')  
scan_db = boto3.resource('dynamodb')
client = boto3.client('ec2')
def lambda_handler(event, context):

    headers = {
        'Content-type': 'application/json',
    }
    url = "https://www.cloudflare.com/ips-v4"
    r = requests.get(url, headers=headers)
    #r.json()
    #print (r.text)
    
    temp = r.text
    cloudflare_IP_list = [y for y in (x.strip() for x in temp.splitlines()) if y] 
    print (cloudflare_IP_list)
    
    
    #Getting IP from already created Managed Prefix List
    prefixlist_response = client.get_managed_prefix_list_entries(
    PrefixListId='pl-4fa04526',
)
    IP_list = []
    for z in prefixlist_response ['Entries']:
        IPs = z ['Cidr']
        IP_lists.append(IPs)
        print("geted from IP list",IPs )
    into_list = list(IP_list)
    print("Converted List",into_list)
    
    
    li = len(s)
    print("Length is",li)

    # l = len(results)
    list1 = cloudflare_IP_list
    list2 = into_list
    compared_list = []
    for ip1 in list1:
        for ip2 in list2:
            if ip1 == ip2:
                print("Matched")
                break
        if ip1 != ip2:
            print("Not matched")
            compared_list.append(ip1)
            print(compared_list)
    print("FInal IP",compared_list)
    ln = len(compared_list)
    print("Lenght of results",ln)
    count = 0
    while count < ln:
        print(compared_list[count])
        response = put_db.put_item(
        TableName='cloudflare',
            Item={
                'IP': {
                'S':compared_list[count],
                
                     },
                }
            ) 
    
        count += 1

    #Getting Final IP List from dynamodb after comparing two lists
    final_ip = []
    table = scan_db.Table("cloudflare")
    response = table.scan()
    for result in response ['Items']:
        results = result ['IP']
        final_ip.append(results)
        print("Result is",results)
    
    # new_lst=(','.join(final_ip))
    # print("New",new_lst)
    
    # typd = type(new_lst)
    # print(typd)
    
    #To remove '' and [] from string
    
    # new_list=(', '.join(final_ip))
    # print("New",new_list)
    # print(new_lst)
    
    # k = "{%s}" % str(new_lst).strip('[]')
    # print("updated",k)
    
    # o = "(%s)" % str(new_list).strip('[]')
    # print("updated",o)
    # print("{}",k)   
    # typs = type(k)
    # print(typs)
    
    target_response = client.describe_managed_prefix_lists(
    PrefixListIds=[
        'pl-03b8f7374414c73bc',
    ]
)
    current_version =  target_response ['PrefixLists'][0]['Version']
    print(current_versionz)

    
    list_to_json = json.dumps(new_lst)
    print(list_to_json)
    
    list_json=[]
    
    for result in compared_list:
        list_json.append({
                'Cidr': result,
                'Description': 'CloudFlare'
         })
    
    
    print (list_json)
    
    response = client.modify_managed_prefix_list(
    PrefixListId='pl-03b8f7374414c73bc',
    CurrentVersion=current_version,
    AddEntries=list_json
       
             )

            