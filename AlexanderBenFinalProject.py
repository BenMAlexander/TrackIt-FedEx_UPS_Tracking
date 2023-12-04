'''
Author - Ben Alexander

Purpose - a program that can take inputted tracking numbers, sort them by shipper and retrieve 
tracking status of the number

See Testing Data at Bottom
'''

import re
import json
import requests 


trackingNumber = input('Enter a tracking number ') #input for testing purposes

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
    
if re.match(fedex, trackingNumber) != None:
        service = 'FedEx'
elif re.match(ups, trackingNumber) != None:
        service = 'UPS'
elif re.match(usps, trackingNumber) != None:
        service = 'USPS'

#print (service) (this is here just for testing purposes. The final code will not have this.)

#This goes into the FedEx API and retrives the information. First it starts with authentication and
#then delevers the results
if service == 'FedEx':
        #Authorization
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
        TrackURL = "https://apis-sandbox.fedex.com/track/v1/trackingNumbers" #searching for tracking information
        TrackHeader ={
            "content-type": "application/json",
            "authorization": "Bearer "+ AuthToken
        }
        TrackBody ={
            "includeDetailedScans": False,
            "trackingInfo": [
                {
                "trackingNumberInfo": {
                    "trackingNumber": trackingNumber
                    }
                }
            ]
        }


        trackingResponse = requests.request("POST",url=TrackURL,data=json.dumps(TrackBody),headers=TrackHeader)

        status = (str(trackingResponse.text)) #Retrieving Results

#This storts the results by status of tracking number. (This needs be be cleaned up, but proof of concept is there.)
        if '"statusByLocale": "In transit",' in status:
            print(trackingNumber, ' is in transit.')

        elif '"statusByLocale": "Picked up",' in status:
            print(trackingNumber, 'is in transit.')

        elif '"statusByLocale": "Clearance Delay",' in status:
            print(trackingNumber, 'is in transit.')

        elif '"statusByLocale": "Initiated",' in status:
            print(trackingNumber, 'is not in transit.')

        elif '"statusByLocale": "Delivery exception",' in status:
            print(trackingNumber, 'has a Delivery Exception.')

        elif '"statusByLocale": "Shipment exception",' in status:
            print(trackingNumber, 'has a Shipping Exception.')

        elif '"statusByLocale": "Delivered",' in status:
            print(trackingNumber, 'has been delivered.')

        elif '"statusByLocale": "Ready for pickup",' in status:
            print(trackingNumber, 'is ready for pickup.')

        elif '"statusByLocale": "Cancelled",' in status:
            print('The shipment for', trackingNumber, 'has been canceled.')

        else:
            print( trackingNumber, 'is not a valid Tracking Number') # This is to cover is something was sorted but not actual a tracking number.
else:
     pass


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

     trackingUrl = "https://wwwcie.ups.com/api/track/v1/details/" + trackingNumber

     query = {
    "locale": "en_US",
    "returnSignature": "false"
    }

     headers = {
    "transId": "string",
    "transactionSrc": "testing",
    "Authorization": "Bearer " + AuthToken
    }

     response = requests.get(trackingUrl, headers=headers, params=query)

     upsStatus = response.json()

     print(upsStatus) #This Section is not finished and needs the results to be sorted out.

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