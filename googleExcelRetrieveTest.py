# encoding: utf-8
import gspread
import json
from oauth2client.client import SignedJwtAssertionCredentials
import csv
# http://gspread.readthedocs.org/en/latest/oauth2.html
# http://stackoverflow.com/questions/20585218/install-python-package-without-root-access 

json_key = json.load(open('googleDocsRetrieveTest-9f78e34059f7.json'))
scope = ['https://spreadsheets.google.com/feeds']

credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
gc = gspread.authorize(credentials)

# Login with your Google account(not provided now...)
# Open a worksheet from spreadsheet with one shot
worksheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/13Y8EbTCLtuBJYQyQ_eXwveac3diD4ToGXpUsMfVSgHw/edit?usp=sharing").sheet1
#worksheet = gc.open("nature").sheet(1);

valueList = worksheet.get_all_values()
print valueList

# Transform to CSV Format

f = open("Questions.csv", "wb")
writer = csv.writer(f)
writer.writerows(valueList)
f.close()
