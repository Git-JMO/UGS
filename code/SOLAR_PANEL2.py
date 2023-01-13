import requests
import numpy as np
import pandas as pd
import codecs
import json
import os
from urllib.request import urlopen
from datetime import date, timedelta,timezone
import datetime as dt
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
import os.path
import simplekml

pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.width',1000)

while True:
    local_time = time.ctime()
    gmt_time=(dt.datetime.now(timezone.utc))
    print (gmt_time)
    print(local_time)

    timenow=(dt.datetime.now(timezone.utc)-dt.timedelta(hours=144))
    last24= timenow.strftime('%Y/%m/%d %H:%M:%S')
    tenMin=(dt.datetime.now(timezone.utc)-dt.timedelta(minutes=10))
    last10_minutes= tenMin.strftime('%Y/%m/%d %H:%M:%S')
    oneMin=(dt.datetime.now(timezone.utc)-dt.timedelta(minutes=2))
    one_minute=oneMin.strftime('%Y/%m/%d %H:%M:%S')
    print(f"This is the last 24 {last24}")

    #url = "https://api.cloudloop.com/DataMo/GetMessagesPolled?token=529b906f-2062-4838-ade0-50eb18bd18a8"
    url = "https://api.cloudloop.com/DataMo/GetMessages?hardware=YAlRXzwrdjymbEKNzxPWKLNxvPkMeqgG&from=2022-12-01T12%3A20%3A00&to=2022-12-25T14%3A20%3A00&token=529b906f-2062-4838-ade0-50eb18bd18a8"

    panel = requests.get(url = url)
    content = json.loads(panel.content)
    #print(content)

    solar_data = pd.DataFrame.from_dict(content['messages'])

    #print(solar_data.columns)

    mystring = (solar_data["payload"])
    ##print(mystring)
    shit=[]
    for row in mystring:
        #print(row)
        str_bytes = bytes(row, encoding = "utf-8")
        #print("fuck")
        #print(str_bytes)
        bin_string = codecs.decode(str_bytes, "hex")
        shit.append(bin_string)
        #print(str(bin_string))
    solar_data["Cleaned Location"] = shit
    solar_data["Cleaned Location"] = solar_data["Cleaned Location"].str.decode("utf-8")
                                                                            
    cleaned_lat = []
    cleaned_lon = []
    for row in solar_data["Cleaned Location"]:
        cleaned_lat.append(row.split(',')[0])
        cleaned_lon.append(row.split(',')[1])
    solar_data["Cleaned Lat"] = cleaned_lat
    solar_data["Cleaned Lon"] = cleaned_lon

    solar_data = solar_data[['txAt',  'id', 'rxAt', 'hardware', 'Cleaned Lat', 'Cleaned Lon']]
     

    # Scraping list of subscribers IOT extract actual device name/id number as they come online

    url_sub = "https://api.cloudloop.com/Sbd/GetSubscribers?query=RockBLOCK&token=529b906f-2062-4838-ade0-50eb18bd18a8"
    panel = requests.get(url = url_sub)
    content = json.loads(panel.content)
    solar_sub = pd.DataFrame.from_dict(content['subscribers'])
    solar_sub = solar_sub[["name", "hardware"]]
    #print(solar_sub)

    # merge Dataframes
    merged_data = solar_data.merge(solar_sub, how = "left", on = "hardware")
    merged_data["rxAt"] = pd.to_datetime(merged_data["rxAt"])
    #print(merged_data)

    #Filter dataframe for last incoming message within the last minute!
    messages_1minutes= (merged_data[(merged_data['rxAt']>=one_minute)])
    #messages_1minutes= (merged_data[(merged_data['rxAt']>=last24)])
    print(f"this is new message dataframe in the last minute {one_minute} GMT")
    print(messages_1minutes)

    messages_1minutes.to_csv("onemin_solar_data_file.csv")

    

    ## convert CSV file to google KML file
    kml=simplekml.Kml()
    messages_1minutes.apply(lambda X: kml.newpoint(name=X['name'],description=X['hardware'],address=X['rxAt'],coords=[(X['Cleaned Lon'],X['Cleaned Lat'])]),axis=1)
    kml.save("merged_solar_data.kml")

    
    recipients=["jonmorales@caci.com","gportes@caci.com", "mandabay3r@proton.me", "christopher.m.white.ctr@socom.mil","bmackes@caci.com","diffa@protonmail.com","john.l.wildt.ctr@mail.mil","sotf.tremor.ugs@protonmail.com"]
    #recipients=["jonmorales@caci.com","gportes@caci.com"]
    recipient=recipients
    sender_email = "ranger1501@outlook.com"
    receiver_email= ",".join(recipients)
    message=MIMEMultipart()
    message['From']=sender_email
    message['To']=receiver_email
    message['Subject']="Solar Panel location information"
    body=MIMEText(f"Solar Panel locational data for the last 24hrs from: {gmt_time}. Any questions please contact SIO.") 
    message.attach(body)
    file ="merged_solar_data.kml"
    dir_path="C:\\Users\Work\Documents\solar"
    files=["merged_solar_data_file.csv","merged_solar_data.kml"]

    for f in files:
        file_path=os.path.join(dir_path,f)
        attachment=MIMEApplication(open(file_path, "rb").read())
        attachment.add_header("Content-Disposition",'attachment', filename=f)
        message.attach(attachment)
    #### this checks to see if there are any messages receive in the last 10 minutes, if so it will send an email with a csv and kml consisting of the last 24hrs of messages
    my_message=message.as_string()

    if messages_1minutes.empty==False:
        
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
    time.sleep(65)

