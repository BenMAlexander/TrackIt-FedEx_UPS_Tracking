'''
Author - Ben Alexander

Purpose - a program that can take inputted tracking numbers, sort them by shipper and retrieve 
tracking status of the number
'''
import re
import json
import requests 
import webbrowser
import tkinter as tk
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk
from tkinter import *

#Setting up path for assets
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\alexa\Documents\GitHub\SDEV140-Assignments\TrackIt\assets")

#Functions ____________________________________________ Functions
#Allows access to files based of path
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

#Deletes entry after submittion
def delete():
    searchbar.delete(3, 'end')

#Opens Manual
def PDF():
    webbrowser.open_new("https://drive.google.com/file/d/1Bw7-fRwVGH0jWDISKnMkt9EmUkxSl2CR/view")

#Sorts entries and returns shipping statuses
def ShippingService():
    service = None
    usps_pattern = [
            '^(94|93|92|94|95)[0-9]{20}$',
            '^(94|93|92|94|95)[0-9]{22}$',
            '^(70|14|23|03)[0-9]{14}$',
            '^(M0|82)[0-9]{8}$',
            '^([A-Z]{2})[0-9]{9}([A-Z]{2})$'
        ]

    ups_pattern = [
            '^(1Z)[0-9A-Z]{16}$',
            '^(T)+[0-9A-Z]{10}$',
            '^[0-9]{9}$',
            '^[0-9]{26}$'
        ]
        
    fedex_pattern = [
            '^[0-9]{20}$',
            '^[0-9]{15}$',
            '^[0-9]{12}$',
            '^[0-9]{22}$'
        ]
        
    usps = "(" + ")|(".join(usps_pattern) + ")"
    fedex = "(" + ")|(".join(fedex_pattern) + ")"
    ups = "(" + ")|(".join(ups_pattern) + ")"
        
    if re.match(usps, trackVar.get()) != None:
            service = 'USPS'
    elif re.match(ups, trackVar.get()) != None:
            service = 'UPS'
    elif re.match(fedex, trackVar.get()) != None:
            service = 'FedEx'
    

    if service == 'FedEx':
        statusR.insert(tk.END, FedExInfo(), '\n'), searchbar.delete(0, 'end')

    elif service == 'UPS':
        statusR.insert(tk.END, UPSInfo(), '\n'), searchbar.delete(0, 'end')

    elif service == 'USPS':
        statusR.insert(tk.END, f'\nUSPS#{trackVar.get()} is not trackable in Track_It!. Check the patch notes for more information.'), searchbar.delete(0, 'end')
    
    elif service == None: #Validation check
        statusR.insert(tk.END, f'\nNumber entered is not a valid tracking Number'), searchbar.delete(0, 'end')


def FedExInfo():
    secretKey = "34beb5df32e246fb8e143a990495a3b6" #Authorization
    publicKey = "l7807fd372290045a6b50466423b3a7b14"
    
    authURL = "https://apis-sandbox.fedex.com/oauth/token" 

    authKeys = {
        "client_id": publicKey,
        "client_secret": secretKey,
        "grant_type": "client_credentials"
    }
    AuthResponse = requests.request("POST",url=authURL,data=authKeys)
    AuthToken = json.loads(AuthResponse.text)["access_token"]

    TrackURL = "https://apis-sandbox.fedex.com/track/v1/trackingnumbers"
    TrackHeader = {
        "content-type": "application/json",
        "authorization": "Bearer "+ AuthToken
    }
    TrackBody = {
        "includeDetailedScans": False, 
        "trackingInfo": [
            {
            "trackingNumberInfo": {
                "trackingNumber": trackVar.get()
                }
            }
        ]
    }

    trackingResponse = requests.request("POST",url = TrackURL,data = json.dumps(TrackBody), headers = TrackHeader)

    trackInfo = (str(trackingResponse.text))

    #Dictionary of FedEx Statuses
    statusId = {
                '"statusByLocale": "In transit",' : 'is In Transit',
                '"statusByLocale": "Delivered",' : 'is Delivered', 
                '"statusByLocale": "Picked up",' : 'is Picked up',
                '"statusByLocale": "Ready for pickup",' : 'is Ready for Pickup',
                '"statusByLocale": "Initiated",' : 'has had a Label Created',
                '"statusByLocale": "Clearance Delay",' : 'has Clearance Delays',
                '"statusByLocale": "Delivery exception",' : 'has Delivery Exceptions',
                '"statusByLocale": "Shipment exception",' : 'has Shipping Exceptions',
                '"statusByLocale": "Cancelled",' : 'is Cancelled',
                }

    for key in list(statusId):
        if key in trackInfo:
            status = f'\nFedEx #{trackVar.get()} {statusId[key]}' #Output string format of status 
            return status  
              

def UPSInfo():
    client_ID = "stMSHwnTtORwszLqtuk75Psec68WFfxtYBHh6yPOyzaO4IRk" #Authorization
    client_Secret = "SDGDXnUXXb7E05vnhbNFACaUMg0Apb239FwTAMp3UGZ3zYGXP8Eb9srrG3e9EMj6"
    authURL = "https://wwwcie.ups.com/security/v1/oauth/token"

    payload = {"grant_type": "client_credentials"}

    headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "x-merchant-id": "G0478G"
    }

    AuthResponse = requests.post(authURL, data = payload, headers = headers, auth = (client_ID, client_Secret))
    AuthToken = json.loads(AuthResponse.text)["access_token"]


    url = "https://onlinetools.ups.com/api/track/v1/details/"+ trackVar.get()

    query = {
    "locale": "en_US",
    "returnSignature": "false"
    }

    headers = {
    "transId": "string",
    "transactionSrc": "testing",
    "Authorization": "Bearer " + AuthToken
    }

    response = requests.get(url, headers = headers, params = query)

    trackInfo = (str(response.json()))
    latestStatus = trackInfo[0 :900]

    #Dicitonary of UPS Statuses
    statusId = {
                "'statusCode': '000'" : 'Status Not Available',
                "'statusCode': '003'" : 'Order Processed: Ready for UPS',
                "'statusCode': '005'" : 'is In Transit',
                "'statusCode': '006'" : 'is On Vehicle for Delivery',
                "'statusCode': '007'" : 'Shipment Information Voided',
                "'statusCode': '010'" : 'is In Transit: On Time',
                "'statusCode': '011'" : 'is Delivered',
                "'statusCode': '012'" : 'Clearance in Progress',
                "'statusCode': '013'" : 'has had an Exception',
                "'statusCode': '014'" : 'has had Clearance Completed',
                "'statusCode': '016'" : 'is Held in Warehouse',
                "'statusCode': '017'" : 'is Held for Customer Pickup',
                "'statusCode': '018'" : 'has had a Delivery Change Requested: Hold',
                "'statusCode': '019'" : 'is Held for Future Delivery',
                "'statusCode': '020'" : 'is Held for Future Delivery Requested',
                "'statusCode': '021'" : 'is On Vehicle for Delivery Today',
                "'statusCode': '022'" : 'has had a First Attempt Made',
                "'statusCode': '023'" : 'has had a Second Attempt Made',
                "'statusCode': '024'" : 'has had a Final Attempt Made',
                "'statusCode': '025'" : 'has Transferred to Local Post Office for Delivery',
                "'statusCode': '026'" : 'has benn Delivered by Local Post Office',
                "'statusCode': '027'" : 'has had a Delivery Address Change Requested',
                "'statusCode': '028'" : 'has had a Delivery Address Changed',
                "'statusCode': '029'" : 'has had a Exception: Action Required',
                "'statusCode': '030'" : 'has had a Local Post Office Exception',
                "'statusCode': '032'" : 'having Adverse Weather May Cause Delay',
                "'statusCode': '033'" : 'has had a Return to Sender Requested',
                "'statusCode': '034'" : 'has Returned to Sender',
                "'statusCode': '035'" : 'is Returning to Sender',
                "'statusCode': '036'" : 'is Returning to Sender: In Transit',
                "'statusCode': '037'" : 'is Returning to Sender: On Vehicle for Delivery',
                "'statusCode': '038'" : 'has been Picked Up',
                "'statusCode': '039'" : 'is In Transit by Post Office',
                "'statusCode': '040'" : 'been Delivered to UPS Access Point Awaiting Customer Pickup',
                "'statusCode': '041'" : 'has had a Service Upgrade Requested',
                "'statusCode': '042'" : 'has had Service Upgraded',
                "'statusCode': '043'" : 'Voided Pickup',
                "'statusCode': '044'" : 'is In Transit to UPS',
                "'statusCode': '045'" : 'has the Order Processed: In Transit to UPS',
                "'statusCode': '046'" : 'has had aDelay',
                "'statusCode': '047'" : 'has had a Delay',
                "'statusCode': '048'" : 'has had a Delay',
                "'statusCode': '049'" : 'has had a Delay: Action Required',
                "'statusCode': '050'" : 'Needs Address Information Required',
                "'statusCode': '051'" : 'has had a Delay: Emergency Situation or Severe Weather',
                "'statusCode': '052'" : 'has had a Delay: Severe Weather',
                "'statusCode': '053'" : 'has had a Delay: Severe Weather, Recovery in Progress',
                "'statusCode': '054'" : 'has had Delivery Change Requested',
                "'statusCode': '055'" : 'has Rescheduled Delivery',
                "'statusCode': '056'" : 'has had a Service Upgrade Requested',
                "'statusCode': '057'" : 'is In Transit to a UPS Access Point',
                "'statusCode': '058'" : 'Clearance Information Required',
                "'statusCode': '059'" : 'has had Damage Reported',
                "'statusCode': '060'" : 'has had a Delivery Attempted',
                "'statusCode': '061'" : 'has had a Delivery Attempted: Adult Signature Required',
                "'statusCode': '062'" : 'has had a Delivery Attempted: Funds Required',
                "'statusCode': '063'" : 'has had a Delivery Change Completed',
                "'statusCode': '064'" : 'Delivery was Refused',
                "'statusCode': '065'" : 'Pickup Attempted',
                "'statusCode': '066'" : 'was Post Office Delivery Attempted',
                "'statusCode': '067'" : 'was Returned to Sender by Post Office',
                "'statusCode': '068'" : 'was Sent to Lost and Found',
                "'statusCode': '069'" : 'Package has Not been Claimed',
                "'message': 'Tracking Information Not Found'": 'Tracking could not be found'
                }

    for key in list(statusId):
        if (key) in latestStatus:
            status = f'\nUPS #{trackVar.get()} {statusId[key]}' #Foramted string for status return
            return status 
        


root = Tk()
#Window Settings
root.geometry("750x500")
root.configure(bg = "#FFFFFF")
root.title('Track_It!')
icon = PhotoImage(file=relative_to_assets("trackitIcon.png"))
root.iconphoto(False, icon)

trackVar = tk.StringVar() #Used to keep tracking number between all functions


#Background/Window ____________________________________________ Background/Window
canvas = Canvas(
    root,
    bg = "#FFFFFF",
    height = 500,
    width = 750,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
background = PhotoImage(
    file = relative_to_assets("background.png"))
image_1 = canvas.create_image(
    375.0,
    250.0,
    image = background
)
#Logo Heading ____________________________________________ Logo Heading
logo = PhotoImage(
    file = relative_to_assets("logo.png"))
trackit_logo = canvas.create_image(
    170.0,
    75.0,
    image = logo
)
slogan = PhotoImage(
    file = relative_to_assets("slogan.png"))
trackit_slogan = canvas.create_image(
    318.0,
    113.0,
    image = slogan
)


#Navigation Buttons ____________________________________________ Navigation Buttons
#Patch Notes Button ____________________________________________ Patch Notes Button
patchNotesButton = PhotoImage(
    file = relative_to_assets("patchNotes2Button.png"))
patch_notes_button  =  Button(
    image = patchNotesButton,
    borderwidth = 0,
    highlightthickness = 0,
    command = lambda: PatchNotes(), #opens up 2nd window
    relief = "flat"
)
patch_notes_button.place(
    x = 64.0,
    y = 128.0,
    width = 83.0,
    height = 20.059642791748047
)

#Manual Button ____________________________________________ Manual Button
manualButton = PhotoImage(
    file = relative_to_assets("ManualButton.png"))
manual_button  =  Button(
    image = manualButton,
    borderwidth = 0,
    highlightthickness = 0,
    command = lambda : PDF(), #Opens pdf of manual
    relief = "flat"
)
manual_button.place(
    x = 154.0,
    y = 128.0,
    width = 81.0,
    height = 21.0
)

#Exit Button ____________________________________________ Exit Button
exitButton = PhotoImage(
    file = relative_to_assets("exitButton.png"))
exit_button = Button(
    image = exitButton,
    borderwidth = 0,
    highlightthickness = 0,
    command = lambda: exit(), #Exits
    relief = "flat"
)
exit_button.place(
    x = 243.0,
    y = 128.0,
    width = 81.0,
    height = 21.0
)


#Search ____________________________________________ Search
#Search Label ____________________________________________ Search Label
canvas.create_text(
    375.0,
    200.0,
    anchor = "center",
    text = "Let’s Track _It! Enter a Tracking Number and press the search button. ", #This was my modifcation for a label. I was having issues making them look good with the background, so opted for this.
    fill = "#D9D9D9",
    font = ("Bayon Regular", 11 * -1)
)

#Searchbar ____________________________________________ Searchbar
searchbarImage = PhotoImage(
    file=relative_to_assets("searchbar.png")) #allowed me to create a more visually appealing entry
searchbar_Image = canvas.create_image(
    380.0,
    221.0,
    image = searchbarImage
)
searchbar  =  Entry(
    root,
    textvariable = trackVar,
    bd = 0,
    bg = "#D9D9D9",
    fg = "#000716",
    highlightthickness = 0
)
searchbar.place(
    x = 184.0,
    y = 212.0,
    width = 392.0,
    height = 16.0
)
#Search Bg ____________________________________________ Search Bg
searchbarBG = PhotoImage(
    file=relative_to_assets("searchbarBG.png")) #Background for Searchbar
searchbar_BG = canvas.create_image(
    374.0,
    220.0,
    image = searchbarBG
)


#Search Button ____________________________________________ Search Button
searchButton = PhotoImage(
    file = relative_to_assets("searchButton.png"))
search_button  =  Button(
    image = searchButton,
    borderwidth = 0,
    highlightthickness = 0,
    command = lambda: ShippingService(), 
    relief = "flat"
)
search_button.place(
    x = 341.0,
    y = 237.0,
    width = 67.0,
    height = 16.0
)


#Status Results ____________________________________________ Status Results 
statusR = Text(
    bd = 0,
    bg = "#ADADAD",
    fg = "#000716",
    highlightthickness=0
)
statusR.place(
    x=136.0,
    y=289.0,
    width = 477.0,
    height = 188.0
)

statusResults = PhotoImage(
    file=relative_to_assets("statusResults.png"))
status_results = canvas.create_image(
    374.5,
    384.0,
    image = statusResults
)

resultsBackground = PhotoImage(
    file=relative_to_assets("resultsBackground.png"))
results_bg = canvas.create_image(
    373.999991126154,
    383.00000770071904,
    image = resultsBackground
)


#Patch Notes Window ____________________________________________ Patch Notes Window        

def PatchNotes(): #2nd window for the Patch Notes
    window = Toplevel()
    window.title('Patch Notes')
    icon = PhotoImage(file=relative_to_assets("trackitIcon.png"))
    window.iconphoto(False, icon)
    window.geometry("400x1000")
    window.configure(bg = "#FFFFFF")
    
    #only way for images to be red in the tkinter function was to make them global.
    global bg
    global trkLogo
    global sub_head
    global unacceptable_pic
    global update_header
    global in_awe_pic

    top = Canvas(
        window,
        bg = "#000000",
        height = 1000,
        width = 400,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    top.place(x = 0, y = 0)
    background = PhotoImage(
        file=relative_to_assets("patchNotesBG.png"))
    bg = top.create_image(
        200.0,
        500.0,
        image=background
    )


    logo = PhotoImage(
        file=relative_to_assets("trackitLogo.png"))
    trkLogo = top.create_image(
        200.0,
        30.0,
        image=logo
    )

    subHeader = PhotoImage(
        file=relative_to_assets("patchNotesSubHeader.png"))
    sub_head = top.create_image(
        200,
        71.0,
        image=subHeader
    )


    #Replacement for Label
    top.create_text(
        25.0,
        97.0,
        anchor="nw",
        text="We are so excited to talk with you about our release\n and to discuss the future plans for TRACK_IT! \n\nWith 1.001 released we know that there is a big elephant \nin the room. Currently TRACK_IT! is not able to assist in \nthe tracking of USPS packages.",
        fill="#FFFFFF",
        font=("Blinker Regular", 14 * -1)
    )

    unacceptablePic = PhotoImage(
        file=relative_to_assets("unacceptable.png"))
    unacceptable_pic = top.create_image(
        200,
        265.0,
        image=unacceptablePic,
    )

    #Replacment for Label
    top.create_text(
        25.0,
        335.0,
        anchor="nw",
        text="With this inconvenience, we at TRACK_IT! are working \ndiligently to close the gaps between us and USPS. Our \ngoal is to give our users the best experiences when \nsearching for their packages. ",
        fill="#FFFFFF",
        font=("Blinker Regular", 14 * -1)
    )

    updateHeader = PhotoImage(
        file=relative_to_assets("updateHeader.png"))
    update_header = top.create_image(
        43.0,
        428.0,
        image=updateHeader
    )

    #Replacement for Label
    top.create_text(
        25.0,
        445.0,
        anchor="nw",
        text="We have delivered visual updates to the client. Instead \nof using TKinter labels, we have transitioned to \n.create_text format. This eliminates the jarring visuals of \nlabels\n\n\n\nand allow a better visual experience.",
        fill="#FFFFFF",
        font=("Blinker Regular", 14 * -1)
    )

    inAwePic = PhotoImage(
        file=relative_to_assets("inAwe.png"))
    in_awe_pic = top.create_image(
        200,
        650.0,
        image=inAwePic
    )

    #Replacement for Label
    top.create_text(
        25.0,
        725.0,
        anchor="nw",
        text="We know, we know, revolutionary idea but that is who \nwe are. \n\nLast note worth mentioning is that we are hoping to \nupdate our tracking status to something a bit more \nmodern. We will be making it easier to pick out the \nstatus of your tracking with a visual update.\n\nThe visual updates and USPS tracking will all be \nreleased in patch 1.5. Until then make sure to keep \nproviding us with feedback. ",
        fill="#FFFFFF",
        font=("Blinker Regular", 14 * -1)
    )

    #Replacement for Label
    top.create_text(
        25.0,
        915.0,
        anchor="nw",
        text="Thank you from all of us at TRACK_IT!",
        fill="#FFFFFF",
        font=("Blinker Regular", 14 * -1)
    )

    exitButton = PhotoImage(
        file = relative_to_assets("exitButton.png"))
    exit_button = Button(
        window,
        image = exitButton,
        borderwidth = 0,
        highlightthickness = 0,
        command = window.destroy, #Only Closes Patch Note Window
        relief = "flat"
    )
    exit_button.place(
        x = 200.0,
        y = 966.0,
        width = 81.0,
        height = 21.0,
        anchor = CENTER
    )

    window.mainloop() #Closes loop for 2nd window
   
root.resizable(False, False) #Main window is not resizable
root.mainloop()
