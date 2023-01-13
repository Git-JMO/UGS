import pandas as pd
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
import os.path
import simplekml
import glob, os
from os import makedirs, path
from pathlib import Path
from datetime import date, timedelta,timezone
import datetime as dt
import time

pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.width',1000)

while True:
    
    local_time = time.ctime()
    gmt_time=(dt.datetime.now(timezone.utc))
    print (gmt_time)
    #print (f'this is current time {local_time}')

## this extract the current day from the calendar and subtracts one day IOT to only create a kmz file for the
# the last 24hrs

    timenow=(dt.datetime.now(timezone.utc)-dt.timedelta(hours=72))
    last24= timenow.strftime('%Y/%m/%d %H:%M:%S')
    tenMin=(dt.datetime.now(timezone.utc)-dt.timedelta(minutes=10))
    last10_minutes= tenMin.strftime('%Y/%m/%d %H:%M:%S')
    oneMin=(dt.datetime.now(timezone.utc)-dt.timedelta(minutes=2))
    one_minute=oneMin.strftime('%Y/%m/%d %H:%M:%S')
    #print(f' this is one minute {one_minute}')
#removed the joined/combined old json file and creates a new one for all dectections

    if os.path.exists('C:\\Users\\Work\\Documents\\messages\\files\out.json'):
        os.remove('C:\\Users\\Work\\Documents\\messages\\files\out.json')
    else:
        print("this file doest not exist")

    folder ='C:\\Users\\Work\\Documents\\messages\\messages'

###File conversion from html to json and create one single json file
    for filename in glob.iglob(os.path.join(folder, '*.html')):
        os.rename(filename, filename[:-5] + '.json')

    file_names = glob.glob('C:\\Users\\Work\\Documents\\messages\\messages\\*.json')

    json_list = []

    for curr_f_name in file_names:
        with open(curr_f_name) as curr_f_obj:
            json_list.append(json.load(curr_f_obj))

    with open('C:\\Users\\Work\\Documents\\messages\\files\\out.json', 'w') as out_file:
        json.dump(json_list, out_file, indent=4)


    with open('C:\\Users\\Work\\Documents\\messages\\files\\out.json','r') as f:
        data = json.loads(f.read())
    df=pd.json_normalize(data)
    df.to_csv("battery.csv")

    #print(df.columns)
    messages=df[['Target.Location.lat', 'Target.Location.lon','Target.Identification.cdifid', 'Target.Identification.number','Target.Identification.description', 'Target.Detection.detecttime','Target.Detection.classification']]

## list of devices by AOR
    
    iraq=['Iridium Ranger 10214', 'Iridium Ranger 10220',
          'Iridium Ranger 10224', 'Iridium Ranger 10226', 'Iridium Ranger 10229',
          'Iridium Ranger 10262','Iridium Ranger 10263', 'Iridium Ranger 10264', 'Iridium Ranger 10265',
          'Iridium Ranger 10266']
    africa=['Iridium Ranger 10268','Iridium Ranger 10269','Iridium Ranger 10270','Iridium Ranger 10271',
            'Iridium Ranger 10272','Iridium Ranger 10273','Iridium Ranger 10274','Iridium Ranger 10275',
            'Iridium Ranger 10276','Iridium Ranger 10277','Iridium Ranger 10277','Iridium Ranger 10286']
    somalia=['Iridium Ranger 10249','Iridium Ranger 10250','Iridium Ranger 10251','Iridium Ranger 10253','Iridium Ranger 10254','Iridium Ranger 10255',
             'Iridium Ranger 10256','Iridium Ranger 10257','Iridium Ranger 10258','Iridium Ranger 10259','Iridium Ranger 10260','Iridium Ranger 10261','Iridium Ranger 10246',
             'Iridium Ranger 10247','Iridium Ranger 10248']
    tester=['10284']


##drops blank values
    messages=messages.dropna(subset=['Target.Location.lat'])
## adds email address column based on AOR; Sotf.tremor.ugs@protonmail.com(iraq), diffa@protonmail.com(africa)
## if device is not in list (iraq/Africa) email will sent to Joe Whitener - fix yourself
    def send_email (row):
        if row['Target.Identification.number']in iraq:
            return ('sotf.tremor.ugs@protonmail.com')
        elif row['Target.Identification.number']in africa:
            return ('diffa@protonmail.com')
        elif row['Target.Identification.number']in somalia:
            return('mandabay3r@proton.me')
        else:
            return ("joseph.whitener@caci.com")
    messages.loc[:,'email']=messages.apply(lambda row:send_email(row), axis=1)

# creates two separate dataframe/excel sheets baed on AOR

    africa_mail= (messages[(messages['email']=='diffa@protonmail.com')])
    iraqi_mail= (messages[(messages['email']=='sotf.tremor.ugs@protonmail.com')])
    somali_mail= (messages[(messages['email']=='mandabay3r@proton.me')])
    tester_mail=(messages[(messages['email']=="joseph.whitener@caci.com")])
    africa_mail=africa_mail.drop('email', axis=1)
    iraqi_mail=iraqi_mail.drop('email', axis=1)
    somali_mail=somali_mail.drop('email', axis=1)
    tester_mail=tester_mail.drop('email',axis=1)
    africa_mail.to_csv("Africom.csv")
    iraqi_mail.to_csv("IZ.csv")
    somali_mail.to_csv("mog.csv")
    tester_mail.to_csv('tester.csv')

#looks for last alerts on file and splits the file for email purposes
    mail=(messages.iloc[-1,7])
    print (mail)

    new_message=(messages[(messages['email']==mail)]) 
    new_message= (new_message[(new_message['Target.Detection.detecttime']>=last24)])
    print("this is new message")
    print(new_message)
    messages_10minutes= (messages[(messages['Target.Detection.detecttime']>=last10_minutes)])
    messages_1minutes= (new_message[(new_message['Target.Detection.detecttime']>=one_minute)])
    print(f"this is new message dataframe in the last minute {one_minute} GMT")
    #print(messages_1minutes)
    print(messages_10minutes)
    print (gmt_time)
    #print(messages.empty)
    #print (messages)
    new_message=new_message.drop('email', axis=1) # drops email column from dataframe
    new_message.to_csv("new_messages.csv")

    recipient=["gportes@caci.com","jonmorales@caci.com", "bmackes@caci.com"]
    if mail=='diffa@protonmail.com':
        recipient.append("diffa@protonmail.com")
    if mail=='sotf.tremor.ugs@protonmail.com':
        recipient.append('sotf.tremor.ugs@protonmail.com')
    if mail=='mandabay3r@proton.me':
        recipient.append('mandabay3r@proton.me')
    if mail=='joseph.whitener@caci.com':
        recipient.append('joseph.whitener@caci.com')

    print (recipient)

## conver CSV file to google KML file

    kml=simplekml.Kml()
    new_message.apply(lambda X: kml.newpoint(name=X['Target.Identification.number'],description=X['Target.Detection.detecttime'],address=X['Target.Detection.classification'],coords=[(X['Target.Location.lon'],X['Target.Location.lat'])]),axis=1)
    kml.save("Rangers_UGS.kml")
##send email to recipients


    #recipients=["jonmorales@caci.com","gportes@caci.com","christopher.m.white.ctr@socom.mil","diffa@protonmail.com","john.l.wildt.ctr@mail.mil","sotf.tremor.ugs@protonmail.com"]
    recipients=recipient
    sender_email = "ranger1501@outlook.com"
    receiver_email= ",".join(recipients)
    message=MIMEMultipart()
    message['From']=sender_email
    message['To']=receiver_email
    message['Subject']="Ranger location information"
    body=MIMEText(f"Ranger locational data for the last 24hrs from: {gmt_time}. Any questions please contact SIO.") 
    message.attach(body)
    file ="Rangers_UGS.kml"
    dir_path="C:/Users/Work/Documents/messages/files"
    files=["new_messages.csv","Rangers_UGS.kml"]

    for f in files:
        file_path=os.path.join(dir_path,f)
        attachment=MIMEApplication(open(file_path, "rb").read())
        attachment.add_header("Content-Disposition",'attachment', filename=f)
        message.attach(attachment)
#### this checks to see if there are any messages receive in the last 10 minutes, if so it will send an email with a csv and kml consisting of the last 24hrs of messages
    my_message=message.as_string()
    #if messages_10minutes.empty==False:

    if messages_1minutes.empty==False:
    #if new_message.empty==False:
    
        
        try:
            with smtplib.SMTP('smtp-mail.outlook.com', 587) as smtpObj:
                smtpObj.ehlo()
                smtpObj.starttls()
                smtpObj.login(sender_email,"Yankees1500")
                smtpObj.sendmail(sender_email,recipients,my_message)
                local_time = time.ctime()
                print (f'your email has been sent successfully {local_time}')
        except Exception as e:
            print (e)
    else:
        print (f"no detection in the last minute :{local_time} ")
    local_time = time.ctime()
    
## this will keep running this code to check for messages every 600 seconds (10 minutes) and send email if there is data in the last 24hrs.
    time.sleep(80)


