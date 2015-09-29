import sys,re
import unicodedata
import ply.lex as lex
import ply.yacc as yacc
import os

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

        #print self.debugfile, self.tabmodule

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)
        
    def processList(self, list):
        for attrib in list:
            if isinstance(attrib,ProductAttribute):
                type  = attrib.get_type()
                value = attrib.get_value()
                print "a[t: %s, v: %s]" % (type, value)
            
    def run(self):
        attribList = None
        with open(self.filename) as fp:
            for line in fp:
                line.rstrip('\n')
                #remove accents - input to normalize must be unicode
                unicode_line  = line.decode('utf8')
                nfkd_line     = unicodedata.normalize('NFKD',unicode_line)
                ascii_line    = nfkd_line.encode('ASCII', 'ignore')
                print "------------------"
                print "%s" % line
                try:
                    attribList = yacc.parse(ascii_line.lower())
                    self.processList (attribList)
                    
                except ParserException as e:
                    print e