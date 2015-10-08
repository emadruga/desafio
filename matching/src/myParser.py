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
        self._model        =  None
        self._line         =  None

    def updateInfo(self,line):
        list = self.getAttributeList()
        self._product      =  next((f for f in list if isinstance(f,ProductAttribute) and f.get_type() == 'product'), None)
        self._product_line =  next((f for f in list if isinstance(f,ProductAttribute) and f.get_type() == 'product_line'), None)
        self._brand        =  next((f for f in list if isinstance(f,ProductAttribute) and f.get_type() == 'brand'), None)
        self._model        =  next((f for f in list if isinstance(f,ProductAttribute) and f.get_type() == 'model'), None)
        self._line         =  line

    def getAttributeList(self):
        return self._alist

    def getLine(self):
        return self._line
        
    def getProductName(self):
        response = None
        if self._product is not None:
            response = self._product.get_value()
        return response
        
    def getProductLine(self):
        response = None
        if self._product_line is not None:
            response = self._product_line.get_value()
        return response
        
    def getProductBrand(self):
        response = None
        if self._brand is not None:
            response =  self._brand.get_value()
        return response
        
    def getProductModel(self):
        response = None
        if self._model is not None:
            response = self._model.get_value()
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
        self.names = { }
        self.filename = kw.get('filename',0)
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"
        self.countProductLine = 0
        self.countModel       = 0
        self.countBrand       = 0
        self.productModelDict     = AutoVivification()
        self.productLineDict      = AutoVivification()
        self.unmatchedProdList = []
        self.matchedProdList = []

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def processList(self, prodList,line):
        # if available, find a model in the  product description
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
                max_model_value = ""
                count = product_line_ix
                model_value = None
                model_value_ix = -1
                contains_digits = re.compile('\d')
                for f in attribList[product_line_ix:]:
                    if isinstance(f,ProductAttribute) and f.get_type() in ('generic','product_line','generic_num'):
                        value = f.get_value()
                        # does attribute value contain digits ?
                        if bool(contains_digits.search(value)): 
                            if (len(value) > len(max_model_value)) and len(value) > 3:
                                max_model_value = value
                                model_value = f
                                model_value_ix = count
                            else:
                                product_line_value += " " + value
                        else:
                            product_line_value += " " + value
                    else:
                        break
                    count += 1
                if model_value is not None and product_line != model_value: 
                    model_value.set_type('model')
                    if brand is not None:
                        if  len(self.productModelDict[brand.get_value()][model_value.get_value()]) == 0:
                            self.productModelDict[brand.get_value()][model_value.get_value()] = [ line ]
                        else:
                            self.productModelDict[brand.get_value()][model_value.get_value()].append(line)
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
                if prod.getProductBrand() is not None:
                    self.countBrand += 1
                if prod.getProductLine() is not None:
                    self.countProductLine += 1
                if prod.getProductModel() is not None:
                    self.countModel += 1
                self.unmatchedProdList.append(prod)
        
    def dump(self):
        print ">"*20
        pprint.pprint(self.productModelDict)
        print "<"*20
        pprint.pprint(self.productLineDict)
        print "=" * 30
        print "Num brands: %d" % self.countBrand
        print "Num product lines: %d" % self.countProductLine
        print "Num models: %d" % self.countModel
        
    def run(self):
        attribList = None
        with open(self.filename) as fp:
            for line in fp:
                line.rstrip('\n')
                #remove accents - input to normalize must be unicode
                unicode_line  = line.decode('utf8')
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
                    sys.stderr.write('<ERROR>: %s\n' % e)

    def _exactModelMatch(self, otherParser):
        assert isinstance(otherParser, Parser)

        unmatchedList = self.unmatchedProdList;
        matchedList   = self.matchedProdList;
        otherDict = otherParser.productModelDict
        for prod in unmatchedList:
            brand = prod.getProductBrand()
            model = prod.getProductModel()
            if (brand is not None) and (model is not None):
                if brand in otherDict:
                    if model in otherDict[brand]:
                        print "Match1: %s/%s" % (brand,model)
                        unmatchedList.remove(prod)
                        matchedList.append(prod)
                    else:
                        print "No Model Match (%s): %s" % (model,prod.getLine())

    def _exactProductLineMatch(self, otherParser):
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
                        print "Match2: %s/%s" % (brand,pline)
                        unmatchedList.remove(prod)
                        matchedList.append(prod)
                    else:
                        print "No Prod Line Match (%s): %s" % (pline,prod.getLine())

    def match(self, comparisonParser):
        assert isinstance(comparisonParser, Parser)

        self._exactModelMatch(comparisonParser)
        self._exactProductLineMatch(comparisonParser)
        print "=" * 30
        print "Num matches:    %d" % len(self.matchedProdList)
        print "Num no matches: %d" % len(self.unmatchedProdList)
                
          
