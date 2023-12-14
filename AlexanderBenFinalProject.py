'''
Author - Ben Alexander

Purpose - a program that can take inputted tracking numbers, sort them by shipper and retrieve 
tracking status of the number

See Testing Data at Bottom
'''

import re
import json
import requests 


trackingNum = input('Enter a tracking number ') #input for testing purposes

service = None #this is used to determin what shipping service was used.

#This section goes through the tracking numbers and sorts them by patterns to determine what shipping service
# the number belongs to.   
usps_patterns = [
        '^(94|93|92|94|95)[0-9]{20}$',
        '^(94|93|92|94|95)[0-9]{22}$',
        '^(70|14|23|03)[0-9]{14}$',
        '^(M0|82)[0-9]{8}$',
        '^([A-Z]{2})[0-9]{9}([A-Z]{2})$'
    ]

ups_patterns = [
        '^(1Z)[0-9A-Z]{16}$',
        '^(T)+[0-9A-Z]{10}$',
        '^[0-9]{9}$',
        '^[0-9]{26}$'
    ]
    
fedex_patterns = [
        '^[0-9]{20}$',
        '^[0-9]{15}$',
        '^[0-9]{12}$',
        '^[0-9]{22}$'
    ]
    
usps = "(" + ")|(".join(usps_patterns) + ")"
fedex = "(" + ")|(".join(fedex_patterns) + ")"
ups= "(" + ")|(".join(ups_patterns) + ")"
    
if re.match(fedex, trackingNum) != None:
        service = 'FedEx'
elif re.match(ups, trackingNum) != None:
        service = 'UPS'
elif re.match(usps, trackingNum) != None:
        service = 'USPS'

#print (service) (this is here just for testing purposes. The final code will not have this.)

#This goes into the FedEx API and retrives the information. First it starts with authentication and
#then delevers the results
if service == 'FedEx':
    secretKey = "34beb5df32e246fb8e143a990495a3b6" #Keys for authorization to FedEx API
    publicKey = "l7807fd372290045a6b50466423b3a7b14"
    
    authURL = "https://apis-sandbox.fedex.com/oauth/token" # Setting up authorization

    authKeys ={
        "client_id": publicKey,
        "client_secret": secretKey,
        "grant_type": "client_credentials"
    }
    AuthResponse = requests.request("POST",url=authURL,data=authKeys)
    AuthToken = json.loads(AuthResponse.text)["access_token"]

    TrackURL = "https://apis-sandbox.fedex.com/track/v1/trackingnumbers"
    TrackHeader ={
        "content-type": "application/json",
        "authorization": "Bearer "+ AuthToken
    }
    TrackBody ={
        "includeDetailedScans": False, 
        "trackingInfo": [
            {
            "trackingNumberInfo": {
                "trackingNumber": trackingNum
                }
            }
        ]
    }

    trackingResponse = requests.request("POST",url=TrackURL,data=json.dumps(TrackBody),headers=TrackHeader)

    trackInfo = (str(trackingResponse.text))

    statusId = {
                '"statusByLocale": "In transit",' : 'In Transit',
                '"statusByLocale": "Delivered",' : 'Delivered', 
                '"statusByLocale": "Picked up",' : 'Picked up',
                '"statusByLocale": "Ready for pickup",' : 'Ready for Pickup',
                '"statusByLocale": "Initiated",' : 'Label Created',
                '"statusByLocale": "Clearance Delay",' : 'Clearance Delay',
                '"statusByLocale": "Delivery exception",' : 'Delivery Exception',
                '"statusByLocale": "Shipment exception",' : 'Shipping Exception',
                '"statusByLocale": "Cancelled",' : 'Cancelled',
                }

    for key in list(statusId):
        if key in trackInfo:
            #status = statusId[key]
            print(statusId[key])


#This goes into the UPS API and retrives the information. First it starts with authentication and
#then delevers the results
if service == 'UPS':
     #Authorization
    client_ID = "stMSHwnTtORwszLqtuk75Psec68WFfxtYBHh6yPOyzaO4IRk"
    client_Secret = "SDGDXnUXXb7E05vnhbNFACaUMg0Apb239FwTAMp3UGZ3zYGXP8Eb9srrG3e9EMj6"
    authURL = "https://wwwcie.ups.com/security/v1/oauth/token"

    payload = {"grant_type": "client_credentials"}

    headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "x-merchant-id": "G0478G"
    }

    AuthResponse = requests.post(authURL, data=payload, headers=headers, auth=(client_ID, client_Secret))
    AuthToken = json.loads(AuthResponse.text)["access_token"]
    data = AuthResponse.json()
    #print(data)


    trackingNum = '1Z4472039095660416'
    url = "https://onlinetools.ups.com/api/track/v1/details/"+ trackingNum

    query = {
    "locale": "en_US",
    "returnSignature": "false"
    }

    headers = {
    "transId": "string",
    "transactionSrc": "testing",
    "Authorization": "Bearer " + AuthToken
    }

    response = requests.get(url, headers=headers, params=query)

    trackInfo = (str(response.json()))
    latestStatus = trackInfo[0 :900]

    statusId = {
                "'statusCode': '000'" : 'Status Not Available',
                "'statusCode': '003'" : 'Order Processed: Ready for UPS',
                "'statusCode': '005'" : 'In Transit',
                "'statusCode': '006'" : 'On Vehicle for Delivery',
                "'statusCode': '007'" : 'Shipment Information Voided',
                "'statusCode': '010'" : 'In Transit: On Time',
                "'statusCode': '011'" : 'Delivered',
                "'statusCode': '012'" : 'Clearance in Progress',
                "'statusCode': '013'" : 'Exception',
                "'statusCode': '014'" : 'Clearance Completed',
                "'statusCode': '016'" : 'Held in Warehouse',
                "'statusCode': '017'" : 'Held for Customer Pickup',
                "'statusCode': '018'" : 'Delivery Change Requested: Hold',
                "'statusCode': '019'" : 'Held for Future Delivery',
                "'statusCode': '020'" : 'Held for Future Delivery Requested',
                "'statusCode': '021'" : 'On Vehicle for Delivery Today',
                "'statusCode': '022'" : 'First Attempt Made',
                "'statusCode': '023'" : 'Second Attempt Made',
                "'statusCode': '024'" : 'Final Attempt Made',
                "'statusCode': '025'" : 'Transferred to Local Post Office for Delivery',
                "'statusCode': '026'" : 'Delivered by Local Post Office',
                "'statusCode': '027'" : 'Delivery Address Change Requested',
                "'statusCode': '028'" : 'Delivery Address Changed',
                "'statusCode': '029'" : 'Exception: Action Required',
                "'statusCode': '030'" : 'Local Post Office Exception',
                "'statusCode': '032'" : 'Adverse Weather May Cause Delay',
                "'statusCode': '033'" : 'Return to Sender Requested',
                "'statusCode': '034'" : 'Returned to Sender',
                "'statusCode': '035'" : 'Returning to Sender',
                "'statusCode': '036'" : 'Returning to Sender: In Transit',
                "'statusCode': '037'" : 'Returning to Sender: On Vehicle for Delivery',
                "'statusCode': '038'" : 'Picked Up',
                "'statusCode': '039'" : 'In Transit by Post Office',
                "'statusCode': '040'" : 'Delivered to UPS Access Point Awaiting Customer Pickup',
                "'statusCode': '041'" : 'Service Upgrade Requested',
                "'statusCode': '042'" : 'Service Upgraded',
                "'statusCode': '043'" : 'Voided Pickup',
                "'statusCode': '044'" : 'In Transit to UPS',
                "'statusCode': '045'" : 'Order Processed: In Transit to UPS',
                "'statusCode': '046'" : 'Delay',
                "'statusCode': '047'" : 'Delay',
                "'statusCode': '048'" : 'Delay',
                "'statusCode': '049'" : 'Delay: Action Required',
                "'statusCode': '050'" : 'Address Information Required',
                "'statusCode': '051'" : 'Delay: Emergency Situation or Severe Weather',
                "'statusCode': '052'" : 'Delay: Severe Weather',
                "'statusCode': '053'" : 'Delay: Severe Weather, Recovery in Progress',
                "'statusCode': '054'" : 'Delivery Change Requested',
                "'statusCode': '055'" : 'Rescheduled Delivery',
                "'statusCode': '056'" : 'Service Upgrade Requested',
                "'statusCode': '057'" : 'In Transit to a UPS Access Point',
                "'statusCode': '058'" : 'Clearance Information Required',
                "'statusCode': '059'" : 'Damage Reported',
                "'statusCode': '060'" : 'Delivery Attempted',
                "'statusCode': '061'" : 'Delivery Attempted: Adult Signature Required',
                "'statusCode': '062'" : 'Delivery Attempted: Funds Required',
                "'statusCode': '063'" : 'Delivery Change Completed',
                "'statusCode': '064'" : 'Delivery Refused',
                "'statusCode': '065'" : 'Pickup Attempted',
                "'statusCode': '066'" : 'Post Office Delivery Attempted',
                "'statusCode': '067'" : 'Returned to Sender by Post Office',
                "'statusCode': '068'" : 'Sent to Lost and Found',
                "'statusCode': '069'" : 'Package Not Claimed',
                }

    for key in list(statusId):
        if (key) in latestStatus:
            print(statusId[key])

    else:
        pass

if service == 'USPS':
     print('This tracking number is USPS.') #I am not able to obtain USPS API Authorization. The program will guide the user to search the unit manually.


'''
Test Data:

FedEx Tracking:
403934084723025 - Arrived at FedEx - In Transit
449044304137821 - Initated (Label Created) - Not in Transit
070358180009382 - Shipment Canceled

UPS Tracking:
1Z12345E0205271688 - Status Code 003 - UPS does not have test shipping numbers. I will find some for final submission.

USPS Tracking:
9400100000000000000000 - Just shows that USPS tracking numbers can be sorted.
''' 
