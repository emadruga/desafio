#!/usr/bin/python
import requests
from lxml import html
import sys
import os
import urllib

from myUtilities import *

url = "http://desafio.sieve.com.br/level5"

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'

myHeaders = { 'User-Agent' : user_agent }

response = requests.get(url,headers = myHeaders)

baseUrl = ""
url = response.url[:-1]
m = re.search('http\:\/\/(.+?)\/', url)
if m:
    baseUrl = m.group(0)
else:
    print "Aborting..."
    sys.exit(1)
basename = os.path.basename(url)
qbasename = urllib.quote(basename)
newUrl = baseUrl + qbasename

myCookies = {'18' : '+' }

response = requests.get(newUrl, headers = myHeaders, cookies = myCookies )
print response.text

tree = html.fromstring(response.text)
list = tree.xpath("//text()")
util = myUtilities()
price = util.price_float(list[0])

print "Price: %+10.2f" % price

