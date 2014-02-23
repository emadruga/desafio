#!/usr/bin/python
import requests
from lxml import html
from myUtilities import *

url = "http://desafio.sieve.com.br/level2"

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'

myHeaders = { 'User-Agent' : user_agent }
myCookies = {'d53db4de415c4e858dc761595623a898' : '+' }

response = requests.get(url,headers = myHeaders, cookies = myCookies)
print response.text

tree = html.fromstring(response.text)

list = tree.xpath("//div/text()")

util = myUtilities()
price = util.price_float(list[0])

print "Price: %+10.2f" % price
