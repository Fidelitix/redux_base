
# coding: utf-8

# In[ ]:




# In[1]:


import os
import requests
import urllib.request
import gzip
import pandas as pd
from datetime import datetime
from datetime import date
import time
dateran = (time.strftime("%d%m%Y"))
#print (dateran)

#CREATE NEW REPORT BEFORE RUNNING SCRIPT, COPY REPORT 116275 ? how can this be automated???

# local main_path = ('/Users/patricktapp/Downloads/') #Insert where you want to have your file inputed, ex: r'/Users/Fidelitix/Documents/''
main_path = ('/home/patricktapp/scripts/') 
url2 = "https://reporting.trader.adgear.com/v1/reports?filters=title=@MonthlyBudget&sort=-id&limit=1" #CHANGE REPORT ID
headers = {'Content-type': 'application/json', 'Authorization' : 'Bearer ptapp:CwvLgPXv8CK7yHy26Yjt'} #Input you Trader username (not email) and API Key
rr = requests.get(url2, headers=headers)

data = rr.json()

url = data[0]['urls'][0]


fullfilename = os.path.join(main_path, 'budget.gz')
urllib.request.urlretrieve(url, fullfilename)

data2 = gzip.open(fullfilename)

monthly = pd.read_csv(data2)

flights = []

for i in range(len(monthly)):
    url = "https://trader.adgear.com/b/106/api/v2/flights/" + str(monthly['flight_id'][i]) + "?auth_token=CwvLgPXv8CK7yHy26Yjt" #Input API token
    r = requests.get(url)
    budget = r.json()
    budget['spend_pacing'] = budget['spend_pacing']['value']
    flights.append(budget)
    
api = pd.DataFrame.from_records(flights)

api = api[['advertiser_id','campaign_id','end_at','start_at','id','name','spend_pacing']]

api.columns = api.columns.str.replace('id','flight_id')

report = pd.merge(monthly, api, on='flight_id')

report.end_at = report.end_at.str[0:10]
report.end_at = report.end_at.apply(lambda d: datetime.strptime(d, "%Y-%m-%d" ))
report.start_at = report.start_at.str[0:10]
report.start_at = report.start_at.apply(lambda d: datetime.strptime(d, "%Y-%m-%d" ))

today = datetime.today()
today = date(today.year,today.month,today.day)
first = date(today.year,today.month,1)
report.end_at = report.end_at.apply(lambda d: date(d.year,d.month,d.day))
report.start_at = report.start_at.apply(lambda d: date(d.year,d.month,d.day))
report['Past Days'] = (today-first).days
report['Days Left'] = report.end_at - today

report['Days Left'] = report['Days Left'].apply(lambda d: d.days)

report['Daily Spend'] = report['buyer_spend']/report['Past Days']
report['Projected Spend'] = report['buyer_spend'] + report['Daily Spend']*report['Days Left']
report['Projected Gap'] = report['spend_pacing'] - report['Projected Spend']

report['month'] = report.end_at.apply(lambda d: d.month)


report = report.loc[report['month'] == today.month]

final_report = report[['advertiser_id','advertiser_name','campaign_id','campaign_name','flight_id','flight_name','buyer_spend','start_at','end_at','spend_pacing','Projected Spend','Projected Gap']]

final_report.to_csv(os.path.join(main_path,'Budget%s.csv')% dateran)  

#print ('success')





# In[2]:

import os, sys

#current_dir = os.listdir(os.getcwd())

# listing directories
# print (current_dir)
# renaming directory ''tutorialsdir"
#os.rename("/Users/patricktapp/Downloads/budget.csv","/Users/patricktapp/Downloads/budget%s.csv" % dateran ) 

#print "Successfully renamed."

# listing directories after renaming "tutorialsdir"
#print "the dir is: %s" %os.listdir(os.getcwd())\


# In[3]:

#send email confirmation with report in attachment

import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

emailfrom = "fidelitix.reporting@gmail.com"
emailto = "info@fidelitix.ca"
# localfileToSend = ("/Users/patricktapp/Downloads/Budget%s.csv" %dateran)
fileToSend = ("/home/patricktapp/scripts/Budget%s.csv" %dateran)

#print (fileToSend)



# In[4]:


username = "fidelitix.reporting@gmail.com"
password = "FxRep0rt"

msg = MIMEMultipart()
msg["From"] = emailfrom
msg["To"] = emailto
msg["Subject"] = "This is the latest budget report"


ctype, encoding = mimetypes.guess_type(fileToSend)
if ctype is None or encoding is not None:
    ctype = "application/octet-stream"

maintype, subtype = ctype.split("/", 1)

if maintype == "text":
    fp = open(fileToSend)
    # Note: we should handle calculating the charset
    attachment = MIMEText(fp.read(), _subtype=subtype)
    fp.close()
elif maintype == "image":
    fp = open(fileToSend, "rb")
    attachment = MIMEImage(fp.read(), _subtype=subtype)
    fp.close()
elif maintype == "audio":
    fp = open(fileToSend, "rb")
    attachment = MIMEAudio(fp.read(), _subtype=subtype)
    fp.close()
else:
    fp = open(fileToSend, "rb")
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(attachment)
attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
msg.attach(attachment)

server_ssl = smtplib.SMTP_SSL("smtp.gmail.com:465")
#server.starttls()
server_ssl.login(username,password)
server_ssl.sendmail(emailfrom, emailto, msg.as_string())
server_ssl.quit()


##import time
## dd/mm/yyyy format
##print (time.strftime("%d/%m/%Y"))


# In[ ]:
