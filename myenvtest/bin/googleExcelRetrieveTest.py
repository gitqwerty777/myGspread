import gspread
import json
import urllib
import logging
from oauth2client.client import SignedJwtAssertionCredentials
from types import *
import sys
import zipfile
import csv
import codecs
import copy
# http://gspread.readthedocs.org/en/latest/oauth2.html
# http://stackoverflow.com/questions/20585218/install-python-package-without-root-access 
# cannot fail-string
# TODO: exe file in windows, downloadFIle and rename
#https://docs.google.com/spreadsheets/d/13Y8EbTCLtuBJYQyQ_eXwveac3diD4ToGXpUsMfVSgHw/edit#gid=0

class LinkFactory:
    def createLink(self, s):
        if s == "None":
            return EmptyLink() 
        else:
            return RealLink(s)
            
class RealLink:
    LINKCOUNT = 0 # static number
    def __init__(self, s):
        self.link = s
    def isLink(self):
        try:
            ret = urllib.urlopen(self.link)
        except:
            return False
        else:
            if ret.code == 200:
                return True
            else:
                return False
                
    def downloadFile(self):
        try:
            f = urllib.URLopener()
            localFilename = "%05d." % RealLink.LINKCOUNT + self.link.split(".")[-1]
            f.retrieve(self.link, localFilename)
            RealLink.LINKCOUNT += 1
        except:
            logger.error("downloadFile Error")
            return ""
        return localFilename
            
class EmptyLink:
    def __init__(self):
        self.link = ""
        self.isEmpty = True
    def isLink(self):
        return True
    def downloadFile(self):
        pass
            
class LinkNotFoundError(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super(LinkNotFoundError, self).__init__(message)
        # Now for your custom code...
        self.errors = errors

linkFactory = LinkFactory()
    
class QuestionDownloader:
    def __init__(self, jsonKeyFile, questionURL, linkPrefix):
        gc = self.Authorize(jsonKeyFile)
        spreadSheet = gc.open_by_url(questionURL)
        self.linkPrefix = linkPrefix
        self.workSheets = spreadSheet.worksheets()        
        self.workSheetName = [w.title for w in self.workSheets]
        
    def Authorize(self, jsonKeyFile):
        json_key = json.load(open(jsonKeyFile))
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
        gc = gspread.authorize(credentials)
        return gc

    def SaveJSONLink(self):
        #self.SaveSheetinJSON(0)
        self.SaveAllSheetsinJSON()
        jsonlinkf = open("JsonLink.json", "w")
        filenamelist = []
        for i in range(len(self.workSheets)):
            filenamelist.append(self.linkPrefix + self.workSheetName[i] + ".json")
        data = json.dumps(filenamelist, separators=(',',':'))
        jsonlinkf.write(data)
        jsonlinkf.close()
                    
    def SaveAllSheetsinJSON(self):
        for i in range(len(self.workSheets)):
            self.SaveSheetinJSON(i)
       
    def transFormType(self, rows):
        for r in rows:   
            for i, element in enumerate(r):
                typei = self.titleList.index(element)
                #print "type of %s is %s" % (r[element], type(r[element]))
                if r[element] == "":
                    pass
                elif type(r[element]) != self.typeList[typei]:
                    r[element] = self.typeList[typei](r[element])
                #print "type of %s is %s" % (r[element], type(r[element]))            
                        
    def SaveSheetinJSON(self, sheetIndex): # Transform CSV to json
        self.LoadWorkSheet(sheetIndex)
        #self.SaveSheetinCSV()
        #f = codecs.open("Questions.csv", 'r', encoding='utf-8')
        #csv_reader = csv.DictReader(f,self.titleList)
        jsonf = codecs.open(self.workSheetName[sheetIndex] + ".json",'w', encoding='utf-8')
        #data = json.dumps([self.transFormType(csv_reader)], indent=4, separators=(',', ': '), ensure_ascii=False, encoding='utf-8')
        data = json.dumps(self.valueStacks, indent=4, separators=(',', ': '), ensure_ascii=False, encoding='utf-8')
        jsonf.write(data)
        #f.close()
        jsonf.close()
        
    def SaveSheetinCSV(self):
        f = codecs.open("Questions.csv", "w", encoding='utf-8')
        writer = csv.writer(f)
        for row in self.valueList:
            for elements in row:
                elements = elements.encode('unicode-escape')                
        writer.writerows(self.valueList)    
        f.close()

    def transFormListType(self, row):
        for i, element in enumerate(row):            
            if element == "":
                pass
            elif type(element) != self.typeList[i]:
                row[i] = self.typeList[i](element)
        return row        
        
    def LoadWorkSheet(self, sheetIndex):
        self.workSheet = self.workSheets[sheetIndex]
        totalList = self.workSheet.get_all_values()

        totalList.pop(0) # first row is chinese
        self.titleList = totalList[0][:]
        strtypeList = totalList[1][:]
        totalList.pop(0) # remove title
        totalList.pop(0) # remove type

        self.typeList = self.LoadType(strtypeList)
        self.valueList = [self.transFormListType(row) for row in totalList if self.checkTypeError(row)]


        # should add original value into array before this
        self.colnum = len(self.typeList)
        newValueList = []
        for i in range(len(self.valueList)):
            nowRow = self.valueList[i]
            for j in range(self.colnum):
                if nowRow[j] != "": # part of array
                    if j == 0:
                        newValueList.append(nowRow)
                        self.updateArray(nowRow)
                        #print nowRow
                        break
                    else:
                        print "original list\n", newValueList[-1]
                        originalValue = newValueList[-1][j-2] 
                        print "original value\n", originalValue                        
                        newList = [originalValue, nowRow[j:]]
                        print "updated value\n", newList
                        newValueList[-1][j-2] = newList
                        print "updated list\n", newValueList[-1]
                        break

        self.valueList = newValueList
        print self.valueList
                
        # reconstruct typelist and titlelist
        typeStack = []
        titleStack = []
        valueStacks = [dict() for i in range(self.colnum)]
        for i, t in enumerate(reversed(self.typeList)):
            if t == ListType: # append later type
                # add upper level list
                typeStack = [typeStack[:]]
                titleStack = [titleStack[:]]
                valueStacks = [{self.titleList[self.colnum-1-i]: valuestack} for valuestack in valueStacks]
            else:
                typeStack.insert(0, t) # push
                titleStack.insert(0, self.titleList[self.colnum-1-i])                
                for j, valueStack in enumerate(valueStacks):
                    valueStack[self.titleList[self.colnum-1-i]] = self.valueList[j][self.colnum-1-i]
        '''
        print "typestack = ", typeStack
        print "titleStack = ", titleStack
        print "valueStack = ", valueStacks'''
        self.valueStacks = valueStacks
                    
                    
    def updateArray(self, row):
        for i in range(len(row), 0, -1):
            pass
        
                    
    def LoadType(self, strtypeList):
        typeList = []
        for elementType in strtypeList:
            if elementType == "int":
                typeList.append(IntType)
            elif elementType == "string":
                typeList.append(UnicodeType)
            elif elementType == "bool":
                typeList.append(BooleanType)
            elif elementType == "float":
                typeList.append(FloatType)
            elif elementType == "array":
                typeList.append(ListType)
            elif elementType == "link":
                typeList.append(InstanceType)
        #print "typelist = ", str(typeList)
        return typeList

    def checkTypeError(self, row):
        for i, element in enumerate(row):
            try:
                if element == "": # TODO:allow empty because of array type
                    pass
                elif(self.typeList[i] == InstanceType):
                    mylink = linkFactory.createLink(element)
                    if not mylink.isLink():
                        raise LinkNotFoundError("link not found", 111)
                    else:
                        newfilename = mylink.downloadFile()
                        row[i] = newfilename # ???
                else:
                    element = self.typeList[i](element)
            except LinkNotFoundError:
                logger.error("%s error: link not found" % (str(row)))
                return False
            except Exception, e:
                logger.error(str(e))
                logger.error("%s error: type of %s(type = %s) not equal to %s" % (str(row), str(element.encode('utf-8')), type(element.encode('utf-8')), self.typeList[i]))
                return False
                
        return True


def getLog():
    logging.basicConfig(filename='questionGetter.log',
                        filemode='w',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s :\n%(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.WARNING)
    return logging.getLogger('QuestionGetter')
        
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    logger = getLog()
    #qd = QuestionDownloader('googleDocsRetrieveTest-9f78e34059f7.json', "https://docs.google.com/spreadsheets/d/13Y8EbTCLtuBJYQyQ_eXwveac3diD4ToGXpUsMfVSgHw/edit?usp=sharing")

    qd = QuestionDownloader('googleDocsRetrieveTest-c415d4b20164.json', "https://docs.google.com/spreadsheets/d/1SAZkS9QY8gF3kNd6UWvNxHrxIYXX6cnbK5-Q_oxqyyk/edit?usp=sharing", "http://140.112.30.38:8000/")
    qd.SaveJSONLink()
    #qd.SaveSheetinJSON(0)
    #z = zipfile.ZipFile('Questions.zip','w',zipfile.ZIP_DEFLATED)
    #z.write('Question0.json')
    #z.close()
    

