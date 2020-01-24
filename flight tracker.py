import requests,datetime, smtplib,ssl,os,re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

x = datetime.datetime.now()
username = os.environ["FLIGHT_AWARE_USERNAME"]
apiKey = os.environ["FLIGHT_AWARE_KEY"]
fxmlUrl = "https://flightxml.flightaware.com/json/FlightXML3/"
def FindFlight(o,d):
    payload = {'origin':o,'destination':d,'type':'auto', 'howMany':'10'}
    response = requests.get(fxmlUrl + "FindFlight", params=payload, auth=(username, apiKey))

    if response.status_code == 200:
        decodedResponse = response.json()
        try:
            for flights in decodedResponse['FindFlightResult']['flights']:
                for fly in flights['segments']:
                    try:
                        print ("{} ({})\t {} ({})\t{} {} ".format(fly['ident'], fly['aircrafttype'], fly['destination']['airport_name'], fly['destination']['code'],fly['filed_departure_time']['date'],fly['filed_departure_time']['time']))
                    except:
                        print('Error with flight')
                print('\n')
        except:
            print('No flights found')
    else:
        print ("There was an error retrieving the data from the server.")

def FlightStatus(flightnum):
    payload = {'ident':flightnum}
    response = requests.get(fxmlUrl + "FlightInfoStatus", params=payload, auth=(username, apiKey))

    if response.status_code == 200:
        decodedResponse = response.json()
        try:
            for fly in decodedResponse['FlightInfoStatusResult']['flights']:
                if fly['filed_departure_time']['date']=='{}/{}/20{}'.format(x.strftime("%d"), x.strftime("%m"), x.strftime("%y")):
                    result= ("{}\t{} {}\t{} {}\t delay: {}\t {}%".format(fly['status'],fly['filed_departure_time']['date'],fly['filed_departure_time']['time'],fly['estimated_arrival_time']['date'],fly['estimated_arrival_time']['time'], fly['arrival_delay'], fly['progress_percent']))
                    print(result)
                    key=input("Would you like to share these details?\nPress y for yes\nPress n for no\n\n")
                    while True:
                        if key=='y':
                            email(result)
                            break
                        elif key=='n':
                            break
                        else:
                            key=input("Sorry thats an invalid input\n\nWould you like to share these details?\nPress y for yes\nPress n for no\n\n")
        except:
            print('Flight not found')
    else:
        print ("There was an error retrieving the data from the server.")

def inputkey():
    key=input('What service do you require?\nPress 0 for Find Flight\nPress 1 for Flight Status\n\n')
    if key == '0':
        FindFlight((input('Origin Airport Code: ').upper()),(input('Destination Airport Code: ').upper()))
    elif key=='1':
        FlightStatus((input('Flight Number: ')).upper())
    else:
        print('Service is not found\n')

def email(result):
    password =os.environ["EMAIL_PASSWORD"]
    sender=os.environ["EMAIL_USERNAME"]
    receiver=input("Recivers email: ")
    regex = r'^\w+[\+\.\w-]*@([\w-]+\.)*\w+[\w-]*\.([a-z]{2,4}|\d+)$'

    while True:
        if re.match(regex,receiver) == None:
            print("Email address is invalid")
            receiver=input("Recivers email: ")
        else:
            break

    message= "Flight Tracking Information:\n{}".format(result)

    msg = MIMEMultipart()
    msg["Subject"] = "Flight Tracking"
    msg["From"] = "Flight Tracker <sender>"
    msg["To"]= (receiver.split("@"))[0]+"<receiver>"

    msg.attach(MIMEText(message, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.sendmail(
            sender, receiver, msg.as_string()
        )

inputkey()