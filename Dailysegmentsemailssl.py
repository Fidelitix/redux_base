
# coding: utf-8

# In[1]:



from ftplib import FTP
import io
import gzip
import requests
import datetime
import smtplib 
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#Segment - Files correspondance
#27922 - MLDB - Honda Accord =3.csv.gz
#27921 - MLDB - Honda Fit = 2.csv.gz
#27920 - MLDB - Honda CR-V = 4.csv.gz
#27919 - MLDB - Honda Civic = 1.csv.gz

#28613 - MLDB - Nissan Rogue = 12.csv.gz
#28610 - MLDB - Nissan Sentra = 15.csv.gz
#28616 - MLDB - Kia Sportage = 16.csv.gz
#28614 - MLDB - Kia Sorento = 17.csv.gz
#28615 - MLDB - Kia Forte = 18.csv.gz
#28612 - MLDB - Nissan Versa = 19.csv.gz
#28611 - MLDB - Nissan Micra = 20.csv.gz



API_Token = 'CwvLgPXv8CK7yHy26Yjt' #replace by your api key in the form: 'api key'
date = str(datetime.date.today())

ftp = FTP('ftp.fidelitix.ca')
ftp.login('datacratic@ftp.fidelitix.ca','D4t4cr4tic')      
ftp.cwd(date)
# If you want to see all files in folder use this:
#listing = []
#ftp.retrlines("LIST", listing.append)


ttl = str(604800) #Time of user expiry in segment in seconds = 7 days 
output = ""

good_files = ['1.csv.gz','2.csv.gz','3.csv.gz','4.csv.gz','12.csv.gz','15.csv.gz','16.csv.gz','17.csv.gz','18.csv.gz','19.csv.gz','20.csv.gz'] #File names containing IDs to push
for i in range(len(good_files)):
    
    if good_files[i] == '1.csv.gz':
        segmentID = str(27919)
    elif good_files[i] == '2.csv.gz':
        segmentID = str(27921)
    elif good_files[i] == '3.csv.gz':
        segmentID = str(27922)
    elif good_files[i] == '4.csv.gz':
        segmentID = str(27920)
    elif good_files[i] == '16.csv.gz':
        segmentID = str(28616)
    elif good_files[i] == '17.csv.gz':
        segmentID = str(28614)
    elif good_files[i] == '18.csv.gz':
        segmentID = str(18615)
    elif good_files[i] == '12.csv.gz':
        segmentID = str(28613)
    elif good_files[i] == '15.csv.gz':
        segmentID = str(28610)
    elif good_files[i] == '19.csv.gz':
        segmentID = str(28612)
    elif good_files[i] == '20.csv.gz':
        segmentID = str(28611)
        
    cmd = 'RETR ' + good_files[i]
    
    sio = io.BytesIO()
    def handle_binary(more_data):
        sio.write(more_data)
        
    resp = ftp.retrbinary(cmd, handle_binary)
    sio.seek(0)
    zippy = gzip.GzipFile(fileobj=sio)
    zippy.seek(0)
    segment = io.TextIOWrapper(zippy)
    segment = segment.read()
    segment = segment.split('\n')
    for k in range(1, len(segment)-1):
        uid = segment[k]
        url = 'https://ss.adgrx.com/api/v1/segments/' + segmentID +'/adgear_uid/' + uid + '?auth_token='+ API_Token + '&ttl=' + ttl
        r = requests.put(url)
        #print(r) #//should print <Response [204]>
    output = output + "\n" + good_files[i]
    output = output + "\t" + str(len(segment)-1)
#print (output)
#import smtplib
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText

fromaddr = "fidelitix.reporting@gmail.com"
toaddr = "patrick.tapp@fidelitix.ca"
msg = MIMEMultipart()
dateran = (time.strftime("%d/%m/%Y"))
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Daily export results %s" % dateran
 
body = "The script ran:\n %s \n\nTHE END" % output
msg.attach(MIMEText(body, 'plain'))
 
server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#server_ssl.starttls()
server_ssl.login(fromaddr, "FxRep0rt")
text = msg.as_string()
server_ssl.sendmail(fromaddr, toaddr, text)
#server_ssl.quit()
server_ssl.close()


# In[ ]:


