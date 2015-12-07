import sys,re
import unicodedata
import ply.lex as lex
import ply.yacc as yacc
import os
import pprint

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value
        
class ParserException(Exception):
    """Exception related to the web service."""

    def __init__(self, type, message):
        self._type = type
        self._message = message

    def __str__(self):
        return self._type + ': ' + self._message

    def get_message(self):
        return self._message

    def get_type(self):
        return self._type

class ProductAttribute(object):
    def __init__(self, t, v):
        self._atype  = t
        self._avalue = v

    def __repr__(self):
        return "a(%r, %r)" % (self._atype, self._avalue)
    
    def get_type(self):
        return self._atype

    def get_value(self):
        return self._avalue

    def set_type(self, t):
        self._atype = t

    def set_value(self, v):
        self._avalue = v

class Product(object):
    def __init__(self, list):
        self._alist = list
        self._product      =  None
        self._product_line =  None
        self._brand        =  None
        self._refcode        =  None
        self._line         =  None

    def updateInfo(self,line):
        list = self.getAttributeList()
        self._product      =  next((f for f in list if isinstance(f,ProductAttribute) and f.get_type() == 'product'), None)
        self._product_line =  next((f for f in list if isinstance(f,ProductAttribute) and f.get_type() == 'product_line'), None)
        self._brand        =  next((f for f in list if isinstance(f,ProductAttribute) and f.get_type() == 'brand'), None)
        self._refcode        =  next((f for f in list if isinstance(f,ProductAttribute) and f.get_type() == 'refcode'), None)
        self._line         =  line

    def getAttributeList(self):
        return self._alist

    def getLine(self):
        return self._line
        
    def getProductType(self):
        # 'smartphone','smart tv','ps3 console', etc
        response = None
        if self._product is not None:
            response = self._product.get_value()
        return response
        
    def getProductLine(self):
        # 'galaxy s4', 'lumia 430 duo', etc.
        response = None
        if self._product_line is not None:
            response = self._product_line.get_value()
        return response
        
    def getProductBrand(self):
        # 'samsung','nokia','apple', etc
        response = None
        if self._brand is not None:
            response =  self._brand.get_value()
        return response
        
    def getProductRefcode(self):
        # 'a1022','xt401', etc
        response = None
        if self._refcode is not None:
            response = self._refcode.get_value()
        return response
        
    def __repr__(self):
        str = "Product ("
        for attrib in self._alist:
            if isinstance(attrib,ProductAttribute):
                str += "%s," % attrib
        str += " )"
        return str
        
class Parser(object):
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.filename = kw.get('filename',0)
        self.tag = kw.get('tag',0)
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.tag + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.dumpfile = modname + ".dump"
        self.infofile = modname + ".info"
        self.tabmodule = modname + "_" + "parsetab"
        self.productRefcodeDict     = AutoVivification()
        self.productLineDict      = AutoVivification()
        self.statsDict            = AutoVivification()
        self.unmatchedProdList = []
        self.matchedProdList = []

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def processList(self, prodList,line):
        # if available, find a refcode in the  product description
        # grow the product line attribute with relevant info.
        if not isinstance(prodList,list):
            return

        for prod in prodList:
            attribList = prod._alist
            brand           = next((f for f in attribList if isinstance(f,ProductAttribute) and f.get_type() == 'brand'), None)
            product_line    = next((f for f in attribList if isinstance(f,ProductAttribute) and f.get_type() == 'product_line'), None)
            if product_line is not None:
                # get first product_line's index
                product_line_value = ""
                product_line_ix = next(i for i, f in enumerate(attribList) if f.get_type() == 'product_line')
                max_refcode_value = ""
                count = product_line_ix
                refcode_value = None
                refcode_value_ix = -1
                contains_digits = re.compile('\d')
                for f in attribList[product_line_ix:]:
                    if isinstance(f,ProductAttribute) and f.get_type() in ('generic','product_line','generic_num'):
                        value = f.get_value()
                        # does attribute value contain digits ?
                        if bool(contains_digits.search(value)): 
                            if (len(value) > len(max_refcode_value)) and len(value) > 3:
                                max_refcode_value = value
                                refcode_value = f
                                refcode_value_ix = count
                            else:
                                product_line_value += " " + value
                        else:
                            product_line_value += " " + value
                    else:
                        break
                    count += 1
                if refcode_value is not None and product_line != refcode_value: 
                    refcode_value.set_type('refcode')
                    if brand is not None:
                        if  len(self.productRefcodeDict[brand.get_value()][refcode_value.get_value()]) == 0:
                            self.productRefcodeDict[brand.get_value()][refcode_value.get_value()] = [ line ]
                        else:
                            self.productRefcodeDict[brand.get_value()][refcode_value.get_value()].append(line)
                if  product_line_value != "" and  product_line_value != product_line.get_value():
                    product_line.set_value(product_line_value.lstrip())
                    lineDict =  self.productLineDict
                    if brand is not None:
                        if  len(lineDict[brand.get_value()][product_line.get_value()]) == 0:
                            lineDict[brand.get_value()][product_line.get_value()] = [ line ]
                        else:
                            lineDict[brand.get_value()][product_line.get_value()].append(line)

                # for attrib in attribList:
                #     if isinstance(attrib,ProductAttribute):
                #         print attrib

    def prepareForMatching(self,prodList, line):
        if prodList is not None:
            for prod in prodList:
                prod.updateInfo(line)
                prodType = prod.getProductType()
                if prodType not in self.statsDict:
                     self.statsDict[prodType]['type']        = 1
                     self.statsDict[prodType]['brand']       = 0
                     self.statsDict[prodType]['productLine'] = 0
                     self.statsDict[prodType]['refcode']       = 0
                else:
                     self.statsDict[prodType]['type']        += 1
                    
                if prod.getProductBrand() is not None:
                    self.statsDict[prodType]['brand']       += 1
                    
                if prod.getProductLine() is not None:
                    self.statsDict[prodType]['productLine'] += 1
                    
                if prod.getProductRefcode() is not None:
                    self.statsDict[prodType]['refcode']       += 1

                self.unmatchedProdList.append(prod)
        
    def dump(self):
        with open(self.dumpfile, "w") as fout:
            print >>fout, ">"*20
            pprint.pprint(self.productRefcodeDict, fout)
            print >>fout, "<"*20
            pprint.pprint(self.productLineDict, fout)
            for prodType in self.statsDict:
                print >>fout, "=" * 30
                print >>fout,"%s: %d"         % (prodType, self.statsDict[prodType]['type'])
                print >>fout,"Num brands: %d" % self.statsDict[prodType]['brand']
                print >>fout,"Num product lines: %d" %  self.statsDict[prodType]['productLine']
                print >>fout,"Num refcodes: %d" %  self.statsDict[prodType]['refcode']
        
    def run(self):
        attribList = None
        with open(self.filename) as fp:
            for line in fp:
                #remove accents - input to normalize must be unicode
                unicode_line  = line.rstrip().decode('utf8')
                nfkd_line     = unicodedata.normalize('NFKD',unicode_line)
                ascii_line    = nfkd_line.encode('ASCII', 'ignore')
                #print "------------------"
                #print "%s" % line
                try:
                    if len(ascii_line) < 500:
                        productList = yacc.parse(ascii_line.lower())
                        self.processList (productList, ascii_line)
                        self.prepareForMatching(productList, ascii_line)
                except ParserException as e:
                    sys.stderr.write('%s\n' % e)

    def _exactRefcodeMatch(self, otherParser,fout):
        assert isinstance(otherParser, Parser)

        unmatchedList = self.unmatchedProdList;
        matchedList   = self.matchedProdList;
        otherDict = otherParser.productRefcodeDict
        for prod in unmatchedList:
            brand = prod.getProductBrand()
            refcode = prod.getProductRefcode()
            if (brand is not None) and (refcode is not None):
                if brand in otherDict:
                    if refcode in otherDict[brand]:
                        print  >>fout, "Match1: %s/%s" % (brand,refcode)
                        unmatchedList.remove(prod)
                        matchedList.append(prod)
                    else:
                        print  >>fout, "No Refcode Match (%s): %s" % (refcode,prod.getLine())
                        
    def _exactProductLineMatch(self, otherParser,fout):
        assert isinstance(otherParser, Parser)

        unmatchedList = self.unmatchedProdList;
        matchedList   = self.matchedProdList;
        otherDict = otherParser.productLineDict
        for prod in unmatchedList:
            brand = prod.getProductBrand()
            pline = prod.getProductLine()
            if (brand is not None) and (pline is not None):
                if brand in otherDict:
                    if pline in otherDict[brand]:
                        print  >>fout, "Match2: %s/%s" % (brand,pline)
                        unmatchedList.remove(prod)
                        matchedList.append(prod)
                    else:
                        print  >>fout, "No Prod Line Match (%s): %s" % (pline,prod.getLine())
    
    def match(self, comparisonParser):
        assert isinstance(comparisonParser, Parser)

        with open(self.infofile, "w") as fout:
            self._exactRefcodeMatch(comparisonParser,fout)
            self._exactProductLineMatch(comparisonParser,fout)
        
            print >>fout, "=" * 30
            print >>fout, "Num matches:    %d" % len(self.matchedProdList)
            print >>fout, "Num no matches: %d" % len(self.unmatchedProdList)
                
    def dumpProdList(self):
        unmatchedList = self.unmatchedProdList;
        for prod in unmatchedList:
            artifact = prod.getProductType()
            brand    = prod.getProductBrand()
            pline    = prod.getProductLine()
            refCode  = prod.getProductRefcode()
            if (artifact is None):
                artifact = "<Sem Artefato>"
            if (brand is None):
                brand = "<Sem Marca>"
            if (pline is None):
                pline = "<Sem Modelo>"
            if (refCode is None):
                refCode = "<Sem Cod Referencia>"
            print  "%s;%s;%s;%s;%s" % (prod.getLine(),"Telefonia", artifact.title(),
                                       brand.title(),pline.upper())
