#encoding: utf-8
'''
work¡Xfrom
workfrom
work\u2014from
work\u2014from
work\u2014from
work\\u2014from
'''

str = u'work\u2014from'
print str
print str.encode('utf-8')
print str.encode('unicode-escape')

str = 'work\u2014from'
print str
print str.encode('utf-8')
print str.decode('utf-8')
print str.encode('unicode-escape')
print str.decode('unicode-escape')

str = ['work\u2014from', u'work\u2014from']
import json
import codecs
jsonf = codecs.open("testunicode1.json",'w', encoding='utf-8')
data = json.dumps(str, indent=4, separators=(',', ': '))
jsonf.write(data)
jsonf.close()

jsonf = codecs.open("testunicode2.json",'w')
data = json.dumps(str, indent=4, separators=(',', ': '))
jsonf.write(data)
jsonf.close()

jsonf = codecs.open("testunicode3.json",'w', encoding='utf-8')
data = json.dumps(str, indent=4, separators=(',', ': '), ensure_ascii=False, encoding='utf-8')
print type(data)
print data
jsonf.write(data)
jsonf.close()


