table = scan_db.Table("Routes")
    response = table.scan()
#    return(response)
    result = response['Items']
    n = []
    for result in response ['Items']:
        results = result ['CIDR']
        n.append(results)
    print(n)
    tee = type(n)
    print(tee)
    che = str(n)
    tyee = type(che)
    print("Type is this", tyee)
    
    table = scan_db.Table("Description")
    response = table.scan()
#    return(response)
    resul = response['Items']
    m = []
    for resul in response ['Items']:
        resu = resul ['Descriptions']
        m.append(resu)
    print(m)
#     #print(results)
    te = type(m)
    print(te)
    ch = str(m)
    tye = type(ch)
    print("Type is", tye)
    ## Adding Routes back to CLient 

    for a in n:
        print(a)
        for b in m:
            response = client.create_client_vpn_route(
        ClientVpnEndpointId=ClientVPNid,
        DestinationCidrBlock=a,
        TargetVpcSubnetId='subnet-f5e5cabd',
        Description=b,
)
    print("Routes has been Added ")
    