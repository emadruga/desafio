#!/usr/bin/python
import requests
from lxml import html
from myUtilities import *

url = "http://desafio.sieve.com.br/level4"

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'

myHeaders = { 'User-Agent' : user_agent }

response = requests.get(url,headers=myHeaders)

myCookies = { 'cade-meu-cookie' : '\"esta aqui\"' }

response = requests.get( response.url, headers = myHeaders, cookies = myCookies )
print response.text

tree = html.fromstring(response.text)
list = tree.xpath("text()")

util = myUtilities()
price = util.price_float(list[0])

print "Price: %+10.2f" % price
