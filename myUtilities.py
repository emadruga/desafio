import sys
import re
import urllib,os
class myUtilities:
	def price_float(self,text):
		price = -99.0
		priceList = re.findall(r"[-+]?[\d*\.\d*\s*]*\,\s*\d+|\d+", text)
		if (len(priceList) > 0):
			priceStr = priceList[0].replace(".","")
			priceStr = priceStr.replace(" ","")
			priceStr = priceStr.replace(",",".")
			price = float(priceStr)
		return price


