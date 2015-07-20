# encoding: utf-8
import gspread
import json
import urllib
import logging
from oauth2client.client import SignedJwtAssertionCredentials
from types import *
import csv
# http://gspread.readthedocs.org/en/latest/oauth2.html
# http://stackoverflow.com/questions/20585218/install-python-package-without-root-access 

logging.basicConfig(filename='questionGetter.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.WARNING)
logger = logging.getLogger('QuestionGetter')

json_key = json.load(open('googleDocsRetrieveTest-9f78e34059f7.json'))
scope = ['https://spreadsheets.google.com/feeds']

credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
gc = gspread.authorize(credentials)

# Login with your Google account(not provided now...)
# Open a worksheet from spreadsheet with one shot
worksheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/13Y8EbTCLtuBJYQyQ_eXwveac3diD4ToGXpUsMfVSgHw/edit?usp=sharing").sheet1
#worksheet = gc.open("nature").sheet(1);

valueList = worksheet.get_all_values()
#print valueList

# Transform to CSV Format
f = open("Questions.csv", "wb")
writer = csv.writer(f)

titleList = valueList[0][:]
strtypeList = valueList[1][:]
valueListWithoutTitle = valueList[:]
valueListWithoutTitle.pop(0) # remove title
valueListWithoutTitle.pop(0) # remove type

LINKCOUNT = 0
class LinkFactory:
    def createLink(self, s):
        if s == "None":
            return EmptyLink() 
        else:
            return RealLink(s)
class RealLink:
    def __init__(self, s):
        self.link = s
    def isLink(self):
        try:
            ret = urllib.urlopen(self.link)
        except:
            print "not link1"
            return False
        else:
            if ret.code == 200:
                return True
            else:
                print "not link"
                return False
                
    def downloadFileFromLink():
        downloadFile = urllib.URLopener()
        localFilename = "%04d." % LINKCOUNT + link.split(".")[-1]
        LINKCOUNT += 1
        print "local file name = %s" % localFilename
        try:
            downloadFile.retrieve(link, localFilename)
        except IOError:
            return ""
        return localFilename
            #if() # connect available    
class EmptyLink:
    def __init__(self):
        self.link = ""
        self.isEmpty = True
    def isLink(self):
        return True
    def downloadFile(self):
        pass
            
typeList = []
for elementType in strtypeList:
    if elementType == "int":
        typeList.append(IntType)
    elif elementType == "string":
        typeList.append(StringType)
    elif elementType == "float":
        typeList.append(FloatType)
    elif elementType == "link":
        typeList.append(InstanceType)
#print "typelist = ", str(typeList)

class LinkNotFoundError(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super(LinkNotFoundError, self).__init__(message)
        # Now for your custom code...
        self.errors = errors

linkFactory = LinkFactory()
def checkTypeError(row):
    for i, element in enumerate(row):
        try:
            if(typeList[i] == InstanceType):
                mylink = linkFactory.createLink(element)
                if not mylink.isLink():
                    raise LinkNotFoundError("link not found", 111)
            else:
                element = typeList[i](element)
        except LinkNotFoundError:
            logger.warning("row %s error:link not found" % str(row))
            return False
        except NameError:
            logger.warning("row %s error:type of %s(type = %s) not equal to %s" % (str(row), str(element), type(element), typeList[i]))
            valueListWithoutTitle.remove(row) #check
            return False
        
    return True

valueListWithoutTitle = [row for row in valueListWithoutTitle if checkTypeError(row)]
    
writer.writerows(valueListWithoutTitle)
f.close()

# Transform CSV to json
fieldnames = valueList[0][:]
f=open("Questions.csv", 'r')
csv_reader = csv.DictReader(f,fieldnames)
json_filename = "Questions.json"
jsonf = open(json_filename,'w')
data = json.dumps([r for r in csv_reader], indent=4, separators=(',', ': '))
jsonf.write(data)
f.close()
jsonf.close()
