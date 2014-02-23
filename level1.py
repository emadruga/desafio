#!/usr/bin/python
import requests
from lxml import html
from myUtilities import *

url = "http://desafio.sieve.com.br/level1"

user_agent = 'Meu agente maneiro, nao compativel com Chrome'

myHeaders = { 'User-Agent' : user_agent }

response = requests.get(url,headers=myHeaders)

print response.text

tree = html.fromstring(response.text)
list = tree.xpath("//div/text()")

util = myUtilities()
price = util.price_float(list[0])

print "Price: %+10.2f" % price

