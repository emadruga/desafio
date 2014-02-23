#!/usr/bin/python
import requests
from lxml import html
import sys
from myUtilities import *

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'
myHeaders = { 'User-Agent' : user_agent }

baseUrl = "http://desafio.sieve.com.br/"
firstBase = "level3"
url = baseUrl + firstBase;

response = requests.get(url,headers = myHeaders)

tree = html.fromstring(response.text)

nextBase = tree.xpath("//a/@href")

nextUrl =  baseUrl + nextBase[0]

response = requests.get(nextUrl,headers = myHeaders)

myCookies = { '18' : '+' }

response = requests.get(url,headers = myHeaders, cookies = myCookies)
print response.text

util = myUtilities()
price = util.price_float(response.text)

print "Price: %+10.2f" % price
